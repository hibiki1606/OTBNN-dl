# OTBNN-dl

[English](/README.md)

OTBNNのポストをダウンロードするためのシンプルなスクリプト集です。

#### 機能:
- あるポスト、もしくはあるユーザーからのポストすべてをmp3ファイルとして保存
- R18、またはNon-R18だけをダウンロードするかをURLから自動的に判定
- すでにダウンロードされたポストはスキップ

#### Todo:
- ファイル名をより正確に処理して、ファイルシステム関連のエラーを減らす

### 使い方
まず最初に、お好きな仮想環境をセットアップして依存関係をインストールしてください。

プログラムは自動的にR18、またはR18でないポスト（達）をダウンロードするかを判定します。
よって、URLを起動引数に指定するだけでダウンロードができます。

いくつかのサンプル:

> あるポストをmp3ファイルとしてダウンロード (-o オプションなしでは、ファイルは*dl*フォルダに自動的に保存されます)
```
python main.py https://example.com/general/cast/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

> あるユーザーのポスト全てを*neko*フォルダにダウンロードする
```
python main.py https://example.com/general/user/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx -o neko
```

> [!IMPORTANT]
> このプロジェクトは私自身と私の友達のために作られたものなので、使用に関する一切の責任は負いません。
> よって、このプロジェクトを使用する際は、必ず**あなた方の判断と責任**で使用してください.

Thanks to Shewi for refactoring the code!
