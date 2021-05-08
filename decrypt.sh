file=".env.json.gpg";
output=".env.json";
gpg --passphrase "$1" --yes --batch -o $output -d $file;
