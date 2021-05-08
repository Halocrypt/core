file=".env.json";

rm  -rf ".env.json.gpg";

gpg --passphrase "$1" --yes --batch -c $file;
