# Welcome to Zaifbot!

zaifに対して自動的に取引を行うbot用のライブラリになります。

ご利用は自己責任でお願いします。

本モジュールはテックビューロ非公式です。



## インストール

1. virtualenvなどで仮想環境を作成しアクティベートします。

2. zaifbotのインストール

※　macの方は予め[homebrew](https://brew.sh/index_ja.html)をインストールしておいてください。

```bash
$ pip install zaifbot  
```

3. zaifbotの初期化

次のコマンドを実行して、データベースを初期化してください。

```bash 
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
