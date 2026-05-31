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

#fileinfo类：存file单个文件的信息
class FileInfo:
    def __init__(self,name,ext,size):
        self.name=name
        self.size=size
        self.ext=ext
    
    def size_kb(self):
        return self.size/1024

#ScanResult类：获取的文件
class ScanResult:
    def __init__(self):
        self.files=[]
    
    def add(self,file_info):
        self.files.append(file_info)
    
    def states_by_ext(self):
        stats={}
        for f in self.files:
            if f.ext not in stats:
                stats[f.ext]={"count":0,"size_kb":0}
            stats[f.ext]["count"] +=1
            stats[f.ext]["size_kb"] +=f.size_kb()
        return stats


def scan_directory(path):
    result=ScanResult()
    for file in Path(path).rglob("*"):
        if file.is_file():
            info=FileInfo(
                file.name,
                file.suffix or "(无拓展名)",
                file.stat().st_size
            )
            result.add(info)
    return result

def print_stats(stats):
    print("\n=== 扫描结果 ===")
    for ext, info in sorted(stats.items()):
        print(f"  {ext:<8} {info['count']:>4} 个    ({info['size_kb']:.1f} KB)")

def export_csv(stats,output_path):
    with open(output_path,"w",newline="",encoding="utf-8-sig") as f:
        write=csv.DictWriter(f,fieldnames=["拓展名","数量","大小KB"])
        write.writeheader()
        for ext,info in stats.items():
            write.writerow({"拓展名":ext,"数量":info["count"],"大小KB":info["size_kb"]})

if args.command =="scan":
    result=scan_directory(args.path)
    stats=result.states_by_ext()
    if args.output:
        try:
            export_csv(stats,args.output)
        except OSError:
            print("导出失败：路径无效或无写入权限")
    else:
        print_stats(stats)