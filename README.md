# VidLift

從 PPTX 簡報匯出內嵌影片，保留原始內容，不重新編碼。

## 安裝和使用

從 GitHub Releases 下載 Windows MSI 安裝檔，雙擊安裝。從桌面或開始功能表開啟「VidLift」，選取 `.pptx` 檔及輸出資料夾，按「匯出影片」。若檔名重複，程式會自動加上編號，不覆蓋已有檔案。可透過 Windows「已安裝的應用程式」解除安裝。

程式處理簡報內嵌在 `ppt/media` 的常見影片格式；外部連結的影片、線上影片和舊式 `.ppt` 檔不會匯出。範例簡報位於 `sample/簡報1.pptx`。

## 從原始碼執行

需要 Windows 和 Python 3.10 以上（含 Tkinter）：

```powershell
python src/vidlift.py
```

## 建置 Windows 安裝檔

需要 Python、PyInstaller 6.22.3、.NET 8 或更新版本，以及 WiX Toolset 5.0.2：

```powershell
python -m pip install pyinstaller==6.22.3
dotnet tool install wix --tool-path .\.tools --version 5.0.2
./scripts/build.ps1 -WixPath ./.tools/wix.exe
```

產物位於 `dist/`。安裝檔為每位使用者安裝，不需要另行安裝 Python。此版本未使用程式碼簽章，Windows 可能顯示發行者無法驗證的提示。
