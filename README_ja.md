# OTBNN-dl

[English](/README.md)

Otobanana / Erovoice-chの投稿をダウンロードするためのシンプルなスクリプト集です。

#### 機能:
- ある投稿、もしくはあるユーザーからの投稿全てをmp3(Otobanana), m4a(Erovoice-ch)ファイルとして保存
- R18、またはNon-R18だけを保存するかをURLから自動的に判定
- すでに保存された投稿はスキップ

> [!NOTE]
> Erovoice-chのサポートは非常に実験的なもので、もしかすると未処理のエラーが発生するかもしれません。  
> プログラムの構造上、Erovoice-chからのダウンロードは非常に低速になります。

#### Todo:
- ファイル名をより正確に処理して、ファイルシステム関連のエラーを減らす

### 使い方
まず最初に、お好きな仮想環境をセットアップして依存関係をインストールしてください。  
Erovoice-chからダウンロードする場合は、ffmpegがインストールされている必要があります。  

プログラムは、自動的にR18、またはR18でない投稿（もしくはあるユーザーからの投稿全て）をダウンロードするかを判定します。
よって、URLを起動引数に指定するだけでダウンロードができます。

いくつかの例:

> ある投稿を保存 (-o オプション無しでは、ファイルは*dl*フォルダに自動的に保存されます。)
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
