""" Script para gerar gráficos do número de casos confirmados, em relação
ao número de testes realizados por cidade na Bahia usando dados da SESAB.

Os dados devem ser baixados do download de base completa no quadro de
situação geral da SESAB:

    https://bi.saude.ba.gov.br/transparencia/

O script usa os bases de casos confirmados, casos descartados e casos
suspeitos e as combina para contar o número de testes realizados.

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
"""
import pandas as pd
import matplotlib.pyplot as plt
from glob import glob
import sys
import os
import argparse
from pathlib import Path
plt.style.use("seaborn")


def plotar_testes_por_cidade(combinado, cidade, data,
                             tamanho_da_janela=7, interativo=False):
    """
    Função para realizar plotagem da quantidade de testes, confirmados e
    a razão dado o conjunto de dados processado.

    Argumentos
    ----------
        combinado : pd.DataFrame
            Conjunto de dados processado pelo programa.

        cidade: str
            Nome da cidade segundo convenções da base de dados. Se setado para
            BAHIA plota todos os dados.

        data : str
            Data pra pôr no título.

        tamanho_da_janela : int
            Tamanho da janela para média móvel. Padrão de 1 semana (7 dias).

        interativo : bool
            Se falso salva a imagem gerada. Se verdadeiro abre interativamente.
            Padrão é falso (salvar).

    Transformação de arquivo
    ------------------------
        Escreve arquivo png do plot se interativo=False.

    Retorno
    -------
        Nada
    """

    # Initial setup
    if cidade != "BAHIA":
        combinado = combinado[combinado["MUNICIPIO DE RESIDENCIA"] == cidade]

    N = combinado.shape[0]

    if N == 0:
        print("Erro: Nenhum registro encontrado. Cidade não está listada ou nome está errado ou fora do padrão aceitado. Gráfico não gerado.")
        return None

    tests = (combinado.resample("1d")["TESTE"].count()).rolling(window=tamanho_da_janela).mean()
    confirmado = combinado.loc[combinado.FONTE == "CONFIRMADOS"].resample("1d")["TESTE"].count().rolling(window=tamanho_da_janela).mean()


    tests = tests[tests > 1]
    confirmado = confirmado[confirmado > 1]
    ratio = confirmado/tests

    # Setting up plot

    fig, [ax, ax2] = plt.subplots(nrows=2, sharex=True, figsize=plt.figaspect(0.66), dpi=110)

    (tests[tests.gt(1)]).plot.area(ax=ax)
    (confirmado[confirmado.gt(1)]).plot.area(ax=ax)
    ratio.plot(ax=ax2)  # Razão num plot secundário

    ax.legend(["Testes feitos", "Confirmados"], loc="upper left")
    ax.set(
        ylabel="Contagem",
        xlabel="Data de notificação",
        title=f"Casos de COVID - {cidade} - BA (Fonte: SESAB, em {data})"
    )
    if cidade == "BAHIA":
        ax.set_title(f"Casos de COVID - {cidade} (Fonte: SESAB, em {data})")

    ax2.set(
        xlabel="Data de notificação",
        ylabel="Razão"
    )

    ax.annotate(f"Total de testes: {N}", xy=(0.72, 0.85), xycoords='axes fraction', weight="bold", fontsize= 12)
    fig.subplots_adjust(hspace=0)
    plt.tight_layout()

    if interativo:
        plt.show()
    else:
        fig.savefig(f"plot_{cidade.replace(' ', '_')}_{data}.png")


if __name__ == "__main__":

    # Coisas do passador de argumentos

    parser = argparse.ArgumentParser()

    parser.add_argument("pasta",
                        help="Pasta onde estão os arquivos da SESAB"
                        )

    parser.add_argument("cidades",
                        nargs="*",
                        help="Cidades para plotar os gráficos"
                        )

    parser.add_argument("--janela", "-j",
                        help="Tamanho da janela para a média móvel",
                        type=int,
                        default=28
                        )

    parser.add_argument("--interativo", "-i",
                        help="Se setado abre os gráficos em modo interativo invés de salvar",
                        action="store_true"
                        )

    args = parser.parse_args()

    # Indo para a pasta
    pasta = sys.argv[1]
    os.chdir(args.pasta)

    # Checando data
    arquivos = glob("Banco Estadual COVID-19*")
    data = arquivos[0].split("_")[-1].split(".")[0]

    # Criar base de dados combinada caso não exista

    if not Path(f"base-de-testes_{data}.csv").exists():

        if len(arquivos) != 3:
            sys.exit("Número de arquivos diferente de 3, cheque os arquivos e rode novamente.")

        chaves = {arquivo.split(" ")[-1].split("_")[0] : arquivo
                  for arquivo in arquivos
                  }

        print(f"Carregando arquivos do dia: {data} \n")

        dados = {
                chave: pd.read_csv(chaves[chave],
                                   delimiter=";",
                                   encoding="ISO-8859-1")
                for chave in chaves
                }

        confirmados = dados["CONFIRMADOS"]
        descartados = dados["DESCARTADOS"]
        suspeitos = dados["SUSPEITOS"]

        confirmados["FONTE"] = "CONFIRMADOS"
        descartados["FONTE"] = "DESCARTADOS"
        suspeitos["FONTE"] = "SUSPEITOS"

        print("Realizando limpeza dos dados")

        # Condição 1: Todos os casos descartados e confirmados foram testados

        confirmados["TESTE"] = True
        descartados["TESTE"] = True

        # Condição 2: Casos suspeitos precisam de confimação através de certas
        # colunas presentes nos dados

        suspeitos["TESTE"] = False  # Inicializando a coluna

        suspeitos["TESTE"] = (
                (~suspeitos["TIPO DE TESTE"].isnull()) |
                (~suspeitos["DATA DA COLETA DO TESTE"].isnull()) |
                (~suspeitos["RESULTADO DO TESTE"].isnull())
        )

        # Por precaução, será usanda informação do ESTADO DO TESTE

        suspeitos.loc[(suspeitos["ESTADO DO TESTE"] == "EXAME NAO SOLICITADO"), ["TESTE"]] = False

        # Montando tabela de testagem.

        colunas_interessantes = [
                "DATA DA NOTIFICACAO",
                "MUNICIPIO DE RESIDENCIA",
                "TESTE",
                "FONTE",
                "DATA DA COLETA DO TESTE"
            ]

        combinar = [
                confirmados[colunas_interessantes],
                descartados[colunas_interessantes],
                suspeitos[colunas_interessantes]
            ]

        combinado = pd.concat(combinar)

        # Condição 3: Dados sem data não podem ser usados para ver tendências
        # no tempo. Devem ser filtrados.

        combinado = combinado[~combinado["DATA DA NOTIFICACAO"].isnull()]

        # Usando representação útil para datas

        combinado['DATA DA NOTIFICACAO'] = pd.to_datetime(
                                combinado['DATA DA NOTIFICACAO'],
                                format='%d/%m/%Y',
                                infer_datetime_format=True
                            )

        # Limpando datas inválidas (apenas 10 achadas)

        combinado = combinado.loc[combinado["DATA DA NOTIFICACAO"].dt.year >= 2020]

        # Salvando no disco
        combinado.to_csv(f"base-de-testes_{data}.csv")

    else:
        # Carregar banco já gerado
        print("\nCarregando base de dados.\n")
        combinado = pd.read_csv(f"base-de-testes_{data}.csv", parse_dates=["DATA DA NOTIFICACAO"])

    combinado = combinado[combinado["TESTE"]]  # Olhando apenas registros com teste
    combinado = combinado.set_index(pd.DatetimeIndex(combinado["DATA DA NOTIFICACAO"]))

    cidades_requisitadas = args.cidades

    for cidade in cidades_requisitadas:
        print(f"Plotando gráficos para a cidade: {cidade}")
        plotar_testes_por_cidade(combinado, cidade, data,
                                 tamanho_da_janela=args.janela,
                                 interativo=args.interativo
                                 )
