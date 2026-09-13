# CCF 状态与检查点：读写 state/run.json、events/events.jsonl 与 checkpoints/（PRD 13）。
# 提供共享工具：时间戳、JSON 读写、简易 YAML 模板解析、id 递推、sha256 校验。
"""CCF 状态层：run 状态、事件日志、检查点、hash 校验。

数据契约与 assets/run.template.json 保持一致；事件日志为 append-only JSONL。
本模块同时承载其它脚本复用的基础工具（模板解析、id 递推、时间戳）。
许可：AGPL-3.0
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(SCRIPT_DIR)
ASSETS_DIR = os.path.join(SKILL_ROOT, "assets")
DEFAULT_STATE_DIR = os.path.join(SKILL_ROOT, "run_state")

RUN_TEMPLATE_NAME = "run.template.json"
PROFILE_TEMPLATE_NAME = "profile.template.json"
YAML_TEMPLATES = (
    "ticket.template.yaml",
    "microtask.template.yaml",
    "artifact.template.yaml",
    "gate-report.template.yaml",
    "integration.template.yaml",
    "delivery.template.yaml",
    "individual.template.yaml",
)


# ---------------------------------------------------------------------------
# 基础工具
# ---------------------------------------------------------------------------
def now_iso() -> str:
    """当前 UTC 时间，ISO8601 格式（Z 结尾）。"""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_dir(path: str) -> str:
    """确保目录存在并返回路径。"""
    os.makedirs(path, exist_ok=True)
    return path


def read_json_file(path: str) -> dict:
    """读取 JSON 文件；不存在返回空字典。"""
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json_file(path: str, data) -> None:
    """写 JSON 文件（UTF-8，ensure_ascii=False，缩进 2）。"""
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


def _to_scalar(raw: str):
    """把模板标量文本转为 Python 值（null/true/false/数字/内联 JSON/字符串）。"""
    s = raw.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'"):
        s = s[1:-1]
    if s == "null":
        return None
    if s == "true":
        return True
    if s == "false":
        return False
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        pass
    if s.startswith("[") and s.endswith("]"):
        try:
            return json.loads(s)
        except Exception:
            pass
    if s.startswith("{") and s.endswith("}"):
        try:
            return json.loads(s)
        except Exception:
            pass
    return s


_KEYVAL_RE = re.compile(r"^([A-Za-z_][\w\-]*):(.*)$")


def _tokenize(text: str):
    toks = []
    for raw in text.splitlines():
        s = raw.replace("\t", "  ")
        if not s.strip() or s.lstrip().startswith("#"):
            continue
        indent = len(s) - len(s.lstrip(" "))
        toks.append((indent, s.strip()))
    return toks


def _parse_block(toks, i: int, indent: int):
    """解析从 toks[i] 开始、首行缩进为 indent 的块；返回 (值, 下一索引)。"""
    if i >= len(toks):
        return None, i
    ind, line = toks[i]
    if ind != indent:
        raise ValueError("模板缩进异常: %r" % line)
    if line.startswith("-"):
        return _parse_list(toks, i, indent)
    kv = _KEYVAL_RE.match(line)
    if kv is None:
        return _to_scalar(line), i + 1
    return _parse_map(toks, i, indent)


def _parse_map(toks, i: int, indent: int):
    node = {}
    while i < len(toks):
        ind, line = toks[i]
        if ind < indent:
            break
        if ind > indent:
            raise ValueError("模板 map 缩进异常: %r" % line)
        kv = _KEYVAL_RE.match(line)
        if kv is None:
            raise ValueError("模板期望 key: value: %r" % line)
        key, val = kv.group(1), kv.group(2).strip()
        if val == "":
            if i + 1 < len(toks) and toks[i + 1][0] > indent:
                child, i = _parse_block(toks, i + 1, toks[i + 1][0])
                node[key] = child
            else:
                node[key] = {}
                i += 1
        else:
            node[key] = _to_scalar(val)
            i += 1
    return node, i


def _parse_list(toks, i: int, indent: int):
    items = []
    while i < len(toks):
        ind, line = toks[i]
        if ind < indent:
            break
        if ind > indent:
            raise ValueError("模板 list 缩进异常: %r" % line)
        if not line.startswith("-"):
            break
        rest = line[1:].strip()
        if rest == "":
            if i + 1 < len(toks) and toks[i + 1][0] > ind:
                child, i = _parse_block(toks, i + 1, toks[i + 1][0])
                items.append(child)
            else:
                items.append(None)
                i += 1
            continue
        kv = _KEYVAL_RE.match(rest)
        if kv is None:
            items.append(_to_scalar(rest))
            i += 1
            continue
        item = {}
        key, val = kv.group(1), kv.group(2).strip()
        if val == "":
            if i + 1 < len(toks) and toks[i + 1][0] > ind:
                child, i = _parse_block(toks, i + 1, toks[i + 1][0])
                item[key] = child
            else:
                item[key] = {}
                i += 1
        else:
            item[key] = _to_scalar(val)
            i += 1
        # 列表项内同一 map 的后续键（缩进 = item 缩进 + 2）
        while i < len(toks):
            cind, cline = toks[i]
            if cind <= ind:
                break
            if cind > ind + 2:
                raise ValueError("模板 list-item 缩进异常: %r" % cline)
            ckv = _KEYVAL_RE.match(cline)
            if ckv is None:
                raise ValueError("模板 list-item 期望 key: %r" % cline)
            ck, cv = ckv.group(1), ckv.group(2).strip()
            if cv == "":
                if i + 1 < len(toks) and toks[i + 1][0] > cind:
                    child, i = _parse_block(toks, i + 1, toks[i + 1][0])
                    item[ck] = child
                else:
                    item[ck] = {}
                    i += 1
            else:
                item[ck] = _to_scalar(cv)
                i += 1
        items.append(item)
    return items, i


def parse_simple_yaml(text: str):
    """解析 CCF assets 模板使用的受限 YAML 子集（key: value、2 空格嵌套、- 列表项）。

    仅用于读取本 Skill 的模板与 manifest，不是通用 YAML 解析器。
    """
    return _parse_block(_tokenize(text), 0, 0)[0]


def load_template(name: str) -> dict:
    """读取 assets 下模板文件，返回字段结构（JSON 模板原样返回，YAML 模板做子集解析）。"""
    path = os.path.join(ASSETS_DIR, name)
    if not os.path.exists(path):
        raise FileNotFoundError("模板缺失: %s" % path)
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    if name.endswith(".json"):
        return json.loads(text)
    if name.endswith(".yaml") or name.endswith(".yml"):
        return parse_simple_yaml(text)
    raise ValueError("不支持的模板类型: %s" % name)


def run_template() -> dict:
    """run.json 模板结构（字段名与 assets/run.template.json 一致）。"""
    return load_template(RUN_TEMPLATE_NAME)


def profile_template() -> dict:
    """profile.json 模板结构。"""
    return load_template(PROFILE_TEMPLATE_NAME)


def format_id(prefix: str, number: int, width: int = 3) -> str:
    """按前缀与位宽拼装编号，如 ('EV', 123, 6) -> 'EV-000123'。"""
    return "%s-%0*d" % (prefix, width, number)


def scan_last_id(path: str, prefix: str) -> int:
    """扫描文件中的 '<prefix>-<数字>' 形编号，返回最大数值；无则 0。"""
    if not os.path.exists(path):
        return 0
    pat = re.compile(re.escape(prefix) + r"-(\d+)")
    last = 0
    with open(path, "r", encoding="utf-8") as fh:
        for raw in fh:
            for m in pat.finditer(raw):
                last = max(last, int(m.group(1)))
    return last


# ---------------------------------------------------------------------------
# 路径
# ---------------------------------------------------------------------------
def resolve_root(root: str | None) -> str:
    """run 工作区根目录；内含 state/、events/、checkpoints/ 三个子目录。"""
    return root if root else DEFAULT_STATE_DIR


def state_file_path(root: str, name: str) -> str:
    return os.path.join(resolve_root(root), "state", name)


def events_dir(root: str) -> str:
    return os.path.join(resolve_root(root), "events")


def events_path(root: str) -> str:
    return os.path.join(events_dir(root), "events.jsonl")


def checkpoints_dir(root: str) -> str:
    return os.path.join(resolve_root(root), "checkpoints")


def run_path(root: str) -> str:
    return state_file_path(root, "run.json")


# ---------------------------------------------------------------------------
# hash
# ---------------------------------------------------------------------------
def compute_hash(data: dict) -> str:
    """对数据（不含 hash 与内部下划线字段）做规范化 JSON 序列化后计算 sha256。"""
    payload = {k: v for k, v in data.items() if k != "hash" and not k.startswith("_")}
    canon = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def verify_hash(data: dict) -> bool:
    """校验数据自带的 hash 是否与内容一致。"""
    return data.get("hash", "") == compute_hash(data)


# ---------------------------------------------------------------------------
# run 状态
# ---------------------------------------------------------------------------
def default_run() -> dict:
    """从模板产出初始 run 状态。"""
    data = run_template()
    data["run_id"] = "CCF-YYYY-MM-DD-NNN"
    data["active"] = True
    data["phase"] = "locked"
    data["theme"] = "light"
    data["style"] = "macos-vibrancy-light-v1"
    data["license"] = "AGPL-3.0"
    data["created_at"] = now_iso()
    data["updated_at"] = now_iso()
    return data


def next_run_id(root: str | None = None) -> str:
    """按 'CCF-YYYY-MM-DD-NNN' 生成递增 run_id。"""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    prefix = "CCF-" + today + "-"
    last = 0
    rp = run_path(root)
    if os.path.exists(rp):
        try:
            run = read_json_file(rp)
            rid = run.get("run_id", "")
            if rid.startswith(prefix):
                last = max(last, int(rid[len(prefix):]))
        except Exception:
            pass
    cp_dir = checkpoints_dir(root)
    if os.path.isdir(cp_dir):
        for fn in os.listdir(cp_dir):
            m = re.match(re.escape(prefix) + r"(\d+)", fn)
            if m:
                last = max(last, int(m.group(1)))
    return "%s%03d" % (prefix, last + 1)


def init_run(root: str | None = None, run_id: str | None = None) -> dict:
    """创建 run 初始状态并写盘；返回 run 字典。"""
    root = resolve_root(root)
    rp = run_path(root)
    if os.path.exists(rp) and read_json_file(rp).get("active", False):
        raise FileExistsError("已有激活中的 run，如需重建请先终止或清空状态目录")
    data = default_run()
    data["run_id"] = run_id if run_id else next_run_id(root)
    ensure_dir(os.path.join(root, "state"))
    save_run(root, data)
    append_event(root, "RUN_INITIALIZED", {"run_id": data["run_id"]})
    return load_run(root)


def load_run(root: str | None = None, verify: bool = True, auto_restore: bool = True) -> dict:
    """读取 state/run.json；不存在时尝试从最近检查点恢复。"""
    root = resolve_root(root)
    rp = run_path(root)
    if not os.path.exists(rp):
        if auto_restore:
            try:
                return restore_checkpoint(root, latest=True)
            except FileNotFoundError:
                pass
        raise FileNotFoundError("未找到 run 状态: %s" % rp)
    run = read_json_file(rp)
    if verify:
        run["_hash_verified"] = verify_hash(run)
    run["_loaded_from"] = "run.json"
    return run


def save_run(root: str | None, run: dict) -> dict:
    """写回 run 状态；更新 updated_at 并计算 hash。"""
    root = resolve_root(root)
    run["updated_at"] = now_iso()
    run["hash"] = compute_hash(run)
    write_json_file(run_path(root), run)
    return run


# ---------------------------------------------------------------------------
# 事件日志（append-only）
# ---------------------------------------------------------------------------
def append_event(root: str | None, name: str, payload=None) -> dict:
    """追加一条事件；返回事件对象。event_id 形如 EV-000123。"""
    root = resolve_root(root)
    ev_path = events_path(root)
    event_id = format_id("EV", scan_last_id(ev_path, "EV") + 1, 6)
    event = {
        "event_id": event_id,
        "name": name,
        "timestamp": now_iso(),
        "payload": payload if payload is not None else {},
    }
    ensure_dir(events_dir(root))
    with open(ev_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=False) + "\n")
    return event


def load_events(root: str | None = None, limit: int | None = None) -> list:
    """读取事件日志（默认最新 N 条，limit=None 返回全部）。"""
    root = resolve_root(root)
    ev_path = events_path(root)
    items = []
    if os.path.exists(ev_path):
        with open(ev_path, "r", encoding="utf-8") as fh:
            for raw in fh:
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    items.append(json.loads(raw))
                except Exception:
                    continue
    if limit is not None:
        return items[-limit:]
    return items


# ---------------------------------------------------------------------------
# 检查点
# ---------------------------------------------------------------------------
def write_checkpoint(root: str | None = None, reason: str = "") -> dict:
    """把当前 run 快照写入 checkpoints/；返回检查点对象。"""
    root = resolve_root(root)
    run = load_run(root, verify=False)
    cp_dir = checkpoints_dir(root)
    ensure_dir(cp_dir)
    ck_id = "CK-%03d" % (1 + len([f for f in os.listdir(cp_dir) if f.startswith("CK-")]))
    cp = {
        "checkpoint_id": ck_id,
        "run_id": run.get("run_id", ""),
        "reason": reason,
        "created_at": now_iso(),
        "hash": run.get("hash", ""),
        "run": run,
    }
    write_json_file(os.path.join(cp_dir, ck_id + ".json"), cp)
    append_event(root, "CHECKPOINT_WRITTEN", {"checkpoint_id": ck_id, "reason": reason})
    return cp


def list_checkpoints(root: str | None = None) -> list:
    """列出全部检查点（按时间升序）。"""
    root = resolve_root(root)
    cp_dir = checkpoints_dir(root)
    out = []
    if os.path.isdir(cp_dir):
        for fn in sorted(os.listdir(cp_dir)):
            if not fn.endswith(".json"):
                continue
            cp = read_json_file(os.path.join(cp_dir, fn))
            if cp:
                out.append({
                    "checkpoint_id": cp.get("checkpoint_id", fn),
                    "run_id": cp.get("run_id", ""),
                    "reason": cp.get("reason", ""),
                    "created_at": cp.get("created_at", ""),
                    "hash": cp.get("hash", ""),
                })
    return sorted(out, key=lambda c: c["checkpoint_id"])


def restore_checkpoint(root: str | None = None, checkpoint_id: str | None = None, latest: bool = False) -> dict:
    """恢复检查点：按 id 或最近一个；校验 hash 后写回 state/run.json。"""
    root = resolve_root(root)
    cp_dir = checkpoints_dir(root)
    if not os.path.isdir(cp_dir):
        raise FileNotFoundError("检查点目录不存在")
    cps = list_checkpoints(root)
    if not cps:
        raise FileNotFoundError("无可用检查点")
    target = None
    if latest:
        target = cps[-1]
    else:
        for c in cps:
            if c["checkpoint_id"] == checkpoint_id:
                target = c
                break
    if target is None:
        raise FileNotFoundError("检查点不存在: %s" % checkpoint_id)
    cp = read_json_file(os.path.join(cp_dir, target["checkpoint_id"] + ".json"))
    run = cp.get("run", {})
    if not run:
        raise ValueError("检查点内容缺失")
    if "hash" in cp and cp.get("hash") != run.get("hash", ""):
        # 检查点内部 hash 与 run 快照 hash 不一致，视为状态漂移
        run["_hash_verified"] = False
    else:
        run["_hash_verified"] = verify_hash(run)
    write_json_file(run_path(root), run)
    append_event(root, "CHECKPOINT_RESTORED", {"checkpoint_id": target["checkpoint_id"]})
    return run


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _build_parser():
    p = argparse.ArgumentParser(description="CCF 状态与检查点工具（PRD 13）")
    p.add_argument("--state-dir", default=None, help="run 工作区根目录（含 state/events/checkpoints）")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("init", help="初始化 run 状态")
    pv = sub.add_parser("view", help="查看当前 run 状态")
    pv.add_argument("--skip-hash", action="store_true", help="跳过 hash 校验")
    pe = sub.add_parser("event", help="追加事件")
    pe.add_argument("--name", required=True, help="事件名")
    pe.add_argument("--payload", default="{}", help="事件 payload（JSON）")
    pc = sub.add_parser("checkpoint", help="写入检查点")
    pc.add_argument("--reason", default="", help="检查点原因")
    pl = sub.add_parser("list", help="列出检查点")
    pr = sub.add_parser("restore", help="恢复检查点")
    pr.add_argument("--id", default=None, help="检查点 id；缺省恢复最近一个")
    ph = sub.add_parser("hash", help="计算 run.json hash 并校验")
    return p


def main(argv=None) -> int:
    args = _build_parser().parse_args(argv)
    root = args.state_dir
    try:
        if args.command == "init":
            run = init_run(root)
            report = {"report": "state-init", "run_id": run["run_id"], "ok": True}
        elif args.command == "view":
            run = load_run(root, verify=not args.skip_hash, auto_restore=False)
            report = {
                "report": "state-view",
                "run_id": run.get("run_id", ""),
                "active": run.get("active", False),
                "phase": run.get("phase", ""),
                "theme": run.get("theme", ""),
                "hash_verified": run.get("_hash_verified", True),
            }
        elif args.command == "event":
            ev = append_event(root, args.name, json.loads(args.payload))
            report = {"report": "state-event", "event": ev}
        elif args.command == "checkpoint":
            cp = write_checkpoint(root, args.reason)
            report = {"report": "state-checkpoint", "checkpoint": {
                "checkpoint_id": cp["checkpoint_id"], "reason": cp["reason"],
                "created_at": cp["created_at"], "hash": cp["hash"]}}
        elif args.command == "list":
            report = {"report": "state-checkpoints", "checkpoints": list_checkpoints(root)}
        elif args.command == "restore":
            run = restore_checkpoint(root, checkpoint_id=args.id,
                                     latest=not bool(args.id))
            report = {"report": "state-restore", "run_id": run.get("run_id", ""),
                      "hash_verified": run.get("_hash_verified", True)}
        elif args.command == "hash":
            run = load_run(root, verify=False, auto_restore=False)
            report = {"report": "state-hash", "hash": run.get("hash", ""),
                      "computed": compute_hash(run), "verified": verify_hash(run)}
    except (FileNotFoundError, FileExistsError, ValueError) as exc:
        report = {"report": "state-error", "ok": False, "message": str(exc)}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("ok", True) else 1


if __name__ == "__main__":
    sys.exit(main())