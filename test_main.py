from main import FileInfo, ScanResult, scan_directory

def test_fileinfo_size_kb():
    f = FileInfo("test.txt", ".txt", 2048, "/tmp/test.txt")
    assert f.size_kb() == 2.0

def test_fileinfo_name():
    f = FileInfo("report.csv", ".csv", 1024, "/tmp/report.csv")
    assert f.name == "report.csv"