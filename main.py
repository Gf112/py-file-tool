import argparse#处理命令行参数
import csv#一个文本文件处理库

parser=argparse.ArgumentParser(description="文件分析工具")
parser.add_argument("command",choices=["scan"],help="要执行的命令")
parser.add_argument("path",help="要扫描的目录路径")
parser.add_argument("--output",help="输出的文件格式")

args=parser.parse_args()
print(f"执行{args.command}，路径：{args.path}")


from pathlib import Path
#从pathlib中导入Path类
#什么是pathlib库：一个面对对象路径处理库

def scan_directory(path):
    states={}
    for file in Path(path).rglob("*"):
        if file.is_file():
            ext=file.suffix or "(无拓展名)"
            if ext not in states:
                states[ext]={"count":0,"size":0}
            states[ext]["count"] +=1
            states[ext]["size"] += file.stat().st_size
    return states

def print_stats(stats):
    print("\n=== 扫描结果 ===")
    for ext, info in sorted(stats.items()):
        size_kb = info["size"] / 1024
        print(f"  {ext:<8} {info['count']:>4} 个    ({size_kb:.1f} KB)")

def export_csv(stats,output_path):
    with open(output_path,"w",newline="",encoding="utf-8-sig") as f:
        write=csv.DictWriter(f,fieldnames=["拓展名","数量","大小KB"])
        write.writeheader()
        for ext,info in stats.items():
            write.writerow({"拓展名":ext,"数量":info["count"],"大小KB":info["size"]/1024})

if args.command =="scan":
    stats=scan_directory(args.path)
    if args.output:
        try:
            export_csv(stats,args.output)
        except OSError:
            print("导出失败：路径无效或无写入权限")
    else:
        print_stats(stats)