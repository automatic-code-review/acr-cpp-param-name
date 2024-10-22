# acr-cpp-param-name

Arquivo config.json

```json
{
  "stage": "static",
  "rules": [
    {
      "message": "Parametro não pode iniciar com o prefixo new, verifique o parametro ${PARAM_NAME}.<br>Arquivo ${FILE_PATH}<br>Linha: ${LINE_NUMBER}",
      "regex": "new.*"
    },
    {
      "message": "Parametro não pode iniciar com a primeira letra maiscula, verifique o parametro ${PARAM_NAME}.<br>Arquivo ${FILE_PATH}<br>Linha: ${LINE_NUMBER}",
      "regex": "[A-Z].*"
    }
  ]
}
```
