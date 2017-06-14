# Welcome to Zaifbot!

zaifに対して自動的に取引を行うbot用のライブラリになります。

ご利用は自己責任でお願いします。

本モジュールはテックビューロ非公式です。



## インストール

1. virtualenvなどで仮想環境を作成しアクティベートします。

2. TA-libのインストール

zaifbotのテクニカル指標はTA-libの実装に依存しています。  
ですので、まず[TA-lib](http://ta-lib.org/hdr_dw.html)をインストールする必要があります。

##### mac OSX

````
brew install ta-lib
````

##### linux 

[ta-lib-0.4.0-src.tar.gz ](http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz)をダウンロードします。

次のコマンドを実行します

```bash
$ untar and cd
$ ./configure --prefix=/usr
$ make
$ sudo make install
```

##### windows

[ta-lib-0.4.0-msvc.zip](http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-msvc.zip)をダウンロードした後、  
``C: \ta-lib``に解凍します。


※詳細は[TA-lib本家](https://github.com/mrjbq7/ta-lib/blob/master/README.md)にてご確認ください。

=============================

3. zaifbotをインストールして初期化します

```bash
$ pip install zaifbot  
$ init_database
```

## 使い方

使い方は[wiki][1]にまとめてありますので、そちらの方をご確認ください。

  [1]: https://github.com/techbureau/zaifbot/wiki

## 開発方法

プルリクエスト大歓迎です。  
また、issue立てたり、wikiの整備なども大変ありがたいです。  
masterに対して記述が追い付いてないwikiもたくさんあります。  

[wikiの開発者向け欄](https://github.com/techbureau/zaifbot/wiki/zaifbot%E9%96%8B%E7%99%BA%E7%92%B0%E5%A2%83%E6%A7%8B%E7%AF%89)を参考に環境を作ってください。
