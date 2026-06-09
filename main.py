from __future__ import annotations
import argparse#处理命令行参数
import csv#一个文本文件处理库
import hashlib


from pathlib import Path
#从pathlib中导入Path类
#什么是pathlib库：一个面对对象路径处理库

#fileinfo类：存file单个文件的信息
class FileInfo:
    def __init__(self, name: str, ext: str, size: int, path: str) -> None:
        self.name: str = name
        self.size: int = size
        self.ext: str = ext
        self.path: str = path

    def size_kb(self) -> float:
        return self.size / 1024

#ScanResult类：获取的文件
class ScanResult:
    def __init__(self) -> None:
        self.files: list[FileInfo] = []

    def add(self, file_info: FileInfo) -> None:
        self.files.append(file_info)

    def find_duplicates(self) -> list[list[str]]:
        """按大小分组 → 同大小算哈希 → 同哈希=重复。返回重复文件组列表。"""
        # 第一步：按大小分组
        by_size: dict[int, list[FileInfo]] = {}
        for f in self.files:
            if f.size not in by_size:
                by_size[f.size] = []
            by_size[f.size].append(f)

        # 第二步：同大小 >1 的组才计算哈希
        duplicates: list[list[str]] = []
        for size, files in by_size.items():
            if len(files) < 2:
                continue
            by_hash: dict[str, list[str]] = {}
            for f in files:
                h = _hash_file(f.path)
                if h not in by_hash:
                    by_hash[h] = []
                by_hash[h].append(f.path)
            # 同哈希 >1 → 重复
            for paths in by_hash.values():
                if len(paths) > 1:
                    duplicates.append(paths)

        return duplicates

    def states_by_ext(self) -> dict[str, dict[str, int | float]]:
        stats: dict[str, dict[str, int | float]] = {}
        for f in self.files:
            if f.ext not in stats:
                stats[f.ext] = {"count": 0, "size_kb": 0.0}
            stats[f.ext]["count"] += 1
            stats[f.ext]["size_kb"] += f.size_kb()
        return stats


def _hash_file(filepath: str) -> str:
    """读取文件内容，返回 MD5 哈希值"""
    h = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def scan_directory(path: str) -> ScanResult:
    result = ScanResult()
    for file in Path(path).rglob("*"):
        if file.is_file():
            info = FileInfo(
                file.name,
                file.suffix or "(无拓展名)",
                file.stat().st_size,
                str(file)
            )
            result.add(info)
    return result

def print_stats(stats: dict[str, dict[str, int | float]]) -> None:
    print("\n=== 扫描结果 ===")
    for ext, info in stats.items():
        print(f"  {ext:<8} {info['count']:>4} 个    ({info['size_kb']:.1f} KB)")

def export_csv(stats: dict[str, dict[str, int | float]], output_path: str) -> None:
    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        write = csv.DictWriter(f, fieldnames=["拓展名", "数量", "大小KB"])
        write.writeheader()
        for ext, info in stats.items():
            write.writerow({"拓展名": ext, "数量": info["count"], "大小KB": info["size_kb"]})

def main():
    parser=argparse.ArgumentParser(
        description="文件分析工具 — 扫描目录，统计文件类型分布",
        epilog="示例:\n  file-scan scan .\n  file-scan scan . --sort size\n  file-scan scan . --dupes\n  file-scan scan . --output result.csv",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("command",choices=["scan"],help="要执行的命令")
    parser.add_argument("path",help="要扫描的目录路径")
    parser.add_argument("--output", metavar="FILE", help="导出 CSV 文件，如 result.csv")
    parser.add_argument("--sort", choices=["size", "count"], default="size", help="排序方式：size=总大小，count=文件数")
    parser.add_argument("--dupes", action="store_true", help="检测重复文件（基于 MD5）")

    args=parser.parse_args()
    print(f"执行{args.command}，路径：{args.path}")

    if args.command =="scan":
        result=scan_directory(args.path)
        if args.dupes:
            dupes = result.find_duplicates()
            if dupes:
                print(f"\n=== 发现 {len(dupes)} 组重复文件 ===")
                for i, group in enumerate(dupes, 1):
                    size_kb = Path(group[0]).stat().st_size / 1024
                    print(f"\n  组{i} ({size_kb:.1f} KB × {len(group)} 份):")
                    for p in group:
                        print(f"    {p}")
            else:
                print("\n=== 未发现重复文件 ===")
            return  # dupes 模式不输出统计表

        stats=result.states_by_ext()
        if args.sort:
            key = "size_kb" if args.sort == "size" else "count"
            stats = dict(sorted(stats.items(), key=lambda kv: kv[1][key], reverse=True))
        else:
            stats = dict(sorted(stats.items()))  # 默认按扩展名排序
        if args.output:
            try:
                export_csv(stats,args.output)
            except OSError:
                print("导出失败：路径无效或无写入权限")
        else:
            print_stats(stats)


if __name__ == "__main__":
    main()
