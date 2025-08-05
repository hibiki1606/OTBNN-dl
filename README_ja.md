# OTBNN-dl

[English](/README.md)

OTBNNの投稿をダウンロードするためのシンプルなスクリプト集です。

#### 機能:
- ある投稿、もしくはあるユーザーからの投稿全てをmp3ファイルとして保存
- R18、またはNon-R18だけを保存するかをURLから自動的に判定
- すでに保存された投稿はスキップ

#### Todo:
- ファイル名をより正確に処理して、ファイルシステム関連のエラーを減らす

### 使い方
まず最初に、お好きな仮想環境をセットアップして依存関係をインストールしてください。

プログラムは、自動的にR18、またはR18でない投稿（もしくはあるユーザーからの投稿全て）をダウンロードするかを判定します。
よって、URLを起動引数に指定するだけでダウンロードができます。

いくつかの例:

> ある投稿をmp3ファイルとして保存 (-o オプション無しでは、ファイルは*dl*フォルダに自動的に保存されます。)
```
python main.py https://example.com/general/cast/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

> あるユーザーの投稿全てを*neko*フォルダに保存
```
python main.py https://example.com/general/user/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx -o neko
```

> [!IMPORTANT]
> このプロジェクトは私自身と私の友達のために作られたものなので、使用に関する一切の責任は負いません。
> よって、このプロジェクトを使用する際は、必ず**あなた方の判断と責任**で使用してください.

Thanks to Shewi for refactoring the code!
