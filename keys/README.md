Unless you need to re-key the SSL certificate, there's no real reason to be here. For documentation's sake:

1. ```clickmd.csr``` and ```clickmd.key``` are the original OpenSSL-generated Certificate Signing Request and private key pair. You can use

    ```$ openssl req -in clickmd.csr -text -noout```

    to see how the CSR was filled out. Then use

    ```$ openssl req -new -newkey rsa:2048 -nodes -keyout newkey.key -out newkey.csr```

    to create a new CSR for the purposes of re-keying. Slight changes are probably acceptable as long as it doesn't conflict with the information given to the Certificate Authority (for instance, at the time of writing the city was not declared, but declaring it wouldn't hurt).

2. [GoDaddy.ca](http://godaddy.ca) was, at the time of writing, where ClickMD buys their certificates. Under the My Products, you can manage our certificate and apply for a rekey. This consists of pasting your new CSR, saving, and then downloading the new certificate chain from them (choose Apache or Other when asked, doesn't matter).

3. Once you have the ZIP file with the certificate chain, you'll need to concatenate one to the other. This is because Flask / Werkzeug does not currently accept intermediate certificates separately; you can, however, chain certificates in a single file. Concatenate the intermediates to the root certificate (order matters here!) by running

    ```cat dcdadbc6b74a1ec1.crt gd_bundle-g2-g1.crt > clickmd.crt```

    ```dcdadbc6b74a1ec1.crt``` was the file name at the time of writing, but you'll likely have a different file name when you re-key.

4. At the bottom of ```app.py``` is where the CRT chain (now clickmd.crt) and your private key (clickmd.key) get declared. Unless you rename these files, you should be good to go now though.