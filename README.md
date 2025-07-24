# Setting up the project

  1. Install Python on your device and add it to the PATH
  2. Install Python Extension in VSCode
  3. Install yfinance and pandas: pip install yfinance pandas or python3 - m pip install yfinance pandas
  4. Install matplotlib
  5. Install moviepy
  6. install opencv-python

Moviepy is a Python lib, using external command tools which makes FFmpeg and ImageMagick mandatory to be installed

  1. Download ffmpeg from web (<https://ffmpeg.org/download.html>) and add it to the PATH (Mac: brew install ffmpeg). Test the installation with ffmpeg -version
  2. Download ImmageMagick from web (<https://imagemagick.org/script/download.php>) and add it to PATH. Test the installation with magick -version

Git Commands:
Neuen branch erstellen zum ausprobieren: git checkout -b dein_branch_name
Branch hochladen: 1. git add .
                  2. git commit -m "nachricht"
                  3. git push origin dein_branch_name
