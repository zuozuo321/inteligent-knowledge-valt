import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("obsidian-mcp")

# Determine vault path from environment variable or default
VAULT_PATH = os.environ.get("VAULT_PATH", "")
if not VAULT_PATH:
    # Fallback: try to find .obsidian folder in common locations
    possible_paths = [
        Path.home() / "knowledge-base",
        Path.home() / "vault",
        Path.home() / "Obsidian",
        Path.home() / "Documents" / "Obsidian Vault",
    ]
    for p in possible_paths:
        if (p / ".obsidian").exists():
            VAULT_PATH = str(p)
            break


@mcp.tool()
def list_notes(folder: str = "") -> str:
    """列出知识库中的笔记文件。

    Args:
        folder: 子目录路径（相对于知识库根目录），为空则列出根目录

    Returns:
        JSON 格式的文件列表，包含路径和最后修改时间
    """
    vault = Path(VAULT_PATH)
    search_dir = vault / folder if folder else vault

    if not search_dir.exists():
        return json.dumps({"error": f"目录不存在: {folder}"}, ensure_ascii=False)

    notes = []
    for f in sorted(search_dir.rglob("*.md")):
        rel_path = f.relative_to(vault)
        mtime = datetime.fromtimestamp(f.stat().st_mtime).isoformat()
        notes.append({
            "path": str(rel_path),
            "name": f.stem,
            "modified": mtime,
            "size": f.stat().st_size
        })

    return json.dumps(notes, ensure_ascii=False, indent=2)


@mcp.tool()
def read_note(note_name: str) -> str:
    """读取指定笔记的完整内容。

    Args:
        note_name: 笔记名称（不含 .md 扩展名，支持相对路径如 "wiki/transformer"）

    Returns:
        笔记的 Markdown 内容
    """
    vault = Path(VAULT_PATH)

    # Try exact path first
    note_path = vault / f"{note_name}.md"
    if note_path.exists():
        return note_path.read_text(encoding="utf-8")

    # Try as relative path
    note_path = vault / note_name
    if note_path.suffix == "":
        note_path = note_path.with_suffix(".md")
    if note_path.exists():
        return note_path.read_text(encoding="utf-8")

    # Search by name in entire vault
    for f in vault.rglob(f"{note_name}.md"):
        return f.read_text(encoding="utf-8")

    return json.dumps({"error": f"未找到笔记: {note_name}"}, ensure_ascii=False)


@mcp.tool()
def search_notes(query: str, folder: str = "") -> str:
    """搜索笔记内容。

    Args:
        query: 搜索关键词（支持大小写不敏感匹配）
        folder: 限定搜索的子目录，为空则搜索整个知识库

    Returns:
        JSON 格式的搜索结果列表，包含文件名、路径和匹配摘要
    """
    vault = Path(VAULT_PATH)
    search_dir = vault / folder if folder else vault

    if not search_dir.exists():
        return json.dumps({"error": f"目录不存在: {folder}"}, ensure_ascii=False)

    results = []
    query_lower = query.lower()

    for f in search_dir.rglob("*.md"):
        try:
            content = f.read_text(encoding="utf-8")
            if query_lower in content.lower():
                rel_path = f.relative_to(vault)
                # Find context around first match
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if query_lower in line.lower():
                        start = max(0, i - 2)
                        end = min(len(lines), i + 3)
                        context = "\n".join(lines[start:end])
                        results.append({
                            "path": str(rel_path),
                            "name": f.stem,
                            "line": i + 1,
                            "context": context.strip()
                        })
                        break
        except Exception:
            continue

    return json.dumps(results, ensure_ascii=False, indent=2)


@mcp.tool()
def create_note(name: str, content: str, folder: str = "") -> str:
    """创建新笔记。

    Args:
        name: 笔记名称（不含 .md 扩展名）
        content: 笔记内容（Markdown 格式）
        folder: 目标文件夹路径（相对于知识库根目录），为空则创建在根目录

    Returns:
        创建结果消息
    """
    vault = Path(VAULT_PATH)

    # Determine target directory
    target_dir = vault / folder if folder else vault
    if not target_dir.exists():
        target_dir.mkdir(parents=True, exist_ok=True)

    note_path = target_dir / f"{name}.md"
    if note_path.exists():
        return json.dumps({"error": f"笔记已存在: {name}", "path": str(note_path)}, ensure_ascii=False)

    note_path.write_text(content, encoding="utf-8")
    return json.dumps({
        "success": True,
        "message": f"笔记已创建: {name}",
        "path": str(note_path.relative_to(vault))
    }, ensure_ascii=False)


@mcp.tool()
def get_tags() -> str:
    """获取知识库中所有使用的标签及其计数。

    Returns:
        JSON 格式的标签列表，包含标签名和出现次数
    """
    vault = Path(VAULT_PATH)
    tag_count = {}

    for f in vault.rglob("*.md"):
        try:
            content = f.read_text(encoding="utf-8")
            # Extract tags from frontmatter
            if content.startswith("---"):
                end = content.find("---", 3)
                if end != -1:
                    frontmatter = content[3:end]
                    for line in frontmatter.split("\n"):
                        line = line.strip()
                        if line.startswith("tags:"):
                            tags_part = line[5:].strip()
                            if tags_part.startswith("[") and tags_part.endswith("]"):
                                # Inline array: tags: [tag1, tag2]
                                tags_inner = tags_part[1:-1]
                                for t in tags_inner.split(","):
                                    t = t.strip().strip('"').strip("'")
                                    if t:
                                        tag_count[t] = tag_count.get(t, 0) + 1
                            else:
                                # List format
                                for t_line in content.split("\n"):
                                    t_line = t_line.strip()
                                    if t_line.startswith("-"):
                                        t = t_line[1:].strip()
                                        if t:
                                            tag_count[t] = tag_count.get(t, 0) + 1
                                    elif t_line.startswith("tags:") and t_line != line:
                                        break
            # Also find inline tags like #tag in content
            for word in content.split():
                if word.startswith("#") and len(word) > 1:
                    tag = word[1:].rstrip(",.;:!?)")
                    if "/" in tag or tag.islower():
                        tag_count[tag] = tag_count.get(tag, 0) + 1
        except Exception:
            continue

    return json.dumps(
        sorted(tag_count.items(), key=lambda x: -x[1]),
        ensure_ascii=False,
        indent=2
    )


@mcp.tool()
def get_backlinks(note_name: str) -> str:
    """查找哪些笔记链接到指定笔记。

    Args:
        note_name: 目标笔记名称（不含 .md 扩展名）

    Returns:
        JSON 格式的反向链接列表
    """
    vault = Path(VAULT_PATH)
    links = []
    search_targets = [
        f"[[{note_name}]]",
        f"[[{note_name}|",
    ]

    for f in vault.rglob("*.md"):
        try:
            content = f.read_text(encoding="utf-8")
            for target in search_targets:
                if target in content:
                    rel_path = f.relative_to(vault)
                    links.append({
                        "source": str(rel_path),
                        "name": f.stem
                    })
                    break
        except Exception:
            continue

    return json.dumps(links, ensure_ascii=False, indent=2)


@mcp.tool()
def get_vault_stats() -> str:
    """获取知识库统计信息。

    Returns:
        JSON 格式的统计信息：笔记总数、总字数、文件夹分布等
    """
    vault = Path(VAULT_PATH)

    total_notes = 0
    total_words = 0
    folder_stats = {}
    orphan_notes = []

    # Collect all note names
    all_note_names = set()
    for f in vault.rglob("*.md"):
        # Skip .obsidian config files
        if ".obsidian" in f.parts:
            continue
        all_note_names.add(f.stem)

    for f in vault.rglob("*.md"):
        if ".obsidian" in f.parts:
            continue

        total_notes += 1
        try:
            content = f.read_text(encoding="utf-8")
            words = len(content.split())
            total_words += words

            rel_dir = str(f.parent.relative_to(vault))
            if rel_dir == ".":
                rel_dir = "/"
            folder_stats[rel_dir] = folder_stats.get(rel_dir, 0) + 1

            # Check if this note is referenced by any other note
            # (Skip root-level files for orphan check)
            if len(f.parts) - len(vault.parts) > 1:
                referenced = False
                content_lower = content.lower()
                for other in vault.rglob("*.md"):
                    if other == f or ".obsidian" in other.parts:
                        continue
                    other_content = other.read_text(encoding="utf-8")
                    if f"[[{f.stem}]]" in other_content or f"[[{f.stem}|" in other_content:
                        referenced = True
                        break
                if not referenced:
                    orphan_notes.append(str(f.relative_to(vault)))

        except Exception:
            continue

    return json.dumps({
        "total_notes": total_notes,
        "total_words": total_words,
        "folder_distribution": dict(sorted(folder_stats.items())),
        "orphan_notes": orphan_notes
    }, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    mcp.run(transport="stdio")