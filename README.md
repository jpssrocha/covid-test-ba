# covid-test-ba

Script para gerar gráficos do número de casos confirmados, em relação
ao número de testes realizados por cidade na Bahia usando dados da SESAB.

Na pasta `demo` existe um vídeo explicando a idéia desta ferramenta.

Os dados devem ser baixados do download de base completa no quadro de
situação geral da SESAB:

    https://bi.saude.ba.gov.br/transparencia/

O script usa os bases de casos confirmados, casos descartados e casos
suspeitos e as combina para contar o número de testes realizados.

EDIT: Esses dados não estão sendo fornecidos pela SESAB atualmente 
(2022-06-21). Na pasta `data` existe a base de dados no dia 24-12-2020.

Tratamento dos dados
--------------------

O conjunto de dados é interpretado no script da seguinte forma:

    1. Casos foram confirmados e descartados com base em testes (logo todos os
    registros são contabilizados como um teste realizado)

    2. Casos suspeitos precisam de confirmação de teste. As palavras chaves
    presentes no banco de dados que podem indicar a realização de um teste
    são:
        - DATA DE COLETA DO TESTE
        - TIPO DE TESTE
        - RESULTADO DO TESTE

        PS: Em geral cerca de 50% dos casos suspeitos não são testados.

    3. Casos sem data de notificação não podem ser inclusos (apenas 0.5% dos
    registros)

Possíveis problemas
-------------------

Esta base de dados não possui chaves primárias, ou seja, uma coluna que
permita identificar cada caso unicamente, portanto não é possível definir
se existem dados duplicados ou mais de um teste realizado para o mesmo caso.

Edit: Nos relatórios das sesab é mostrado um diagrama do processo de aquisição
desses dados onde contém uma remoção de duplicatas. Portanto este problema já é
tratado na fonte dos dados.


Uso básico
----------

    O script deve ser rodado de dentro da pasta onde estão os dados. Dentro
    desta pasta deve haver os dados de apenas um dia com a mesma nomenclatura
    que são tirados do site. Da linha de comando rodar:

        $ python covid_tests_sesab.py <nome_da_pasta> <nomes_das_cidades>

    O nome das cidades deve ser passado no padrão adotado na base de dados,
    ou seja, em maiúsculo e sem acentos. Usar "c" no lugar de "ç".

    Nomes compostos devem ser passados entre aspas. E o nome da pasta deve
    ser necessariamente passado primeiro.

    Por padrão será sempre criado um arquivo csv com os dados finais que é
    reutilizado para gerar novos plots rapidamente.

    Se invés de o nome de uma cidade for passado BAHIA o programa irá gerar
    um gráfico com todos os dados.

    Para mais detalhes sobre os parâmetros usar:

        $ python covid_tests_sesab.py  -h


Exemplos
--------

    Para salvar os gráficos para Itabuna, Ilhéus e Porto Seguro numa pasta
    chamada dados:

        $ python covid_tests_sesab.py  dados ITABUNA ILHEUS "PORTO SEGURO"

    Para plotar gráficos de Itabuna e Ilhéus interativamente na pasta atual:

        $ python covid_tests_sesab.py  . ITABUNA ILHEUS -i

    Para plotar gráficos de Itabuna e Ilhéus interativamente na pasta atual com
    a média móvel em uma janela de 14 dias.

        $ python covid_tests_sesab.py . ITABUNA ILHEUS -i -j 14

    Para plotar gráficos toda a Bahia interativamente na pasta atual com
    a média móvel em uma janela de 21 dias.

        $ python covid_tests_sesab.py . BAHIA -i -j 21

Pacotes necessários
-------------------

- python >= 3.8
- pandas >= 1.0.5
- matplot>ib >= 3.2.2

Contato
-------

    Email: joaopedro0498@hotmail.com
