import pandas
import numpy as np
import matplotlib.pyplot as plt

candidates = pandas.read_csv("1976-2020-president.csv")

# 1. Urči pořadí jednotlivých kandidátů v jednotlivých státech a v jednotlivých letech (pomocí metody rank()).
# Nezapomeň, že data je před použitím metody nutné seřadit a spolu s metodou rank() je nutné použít metodu groupby().
candidates = candidates.sort_values(["year","state"])
candidates["rank"] = candidates.groupby(["year", "state"])["candidatevotes"].rank(ascending=False)
print(candidates.head(15))

# 2. Pro další analýzu jsou důležití pouze vítězové. Vytvoř novou tabulku, která bude obsahovat pouze vítěze voleb.
winners = candidates[candidates["rank"] == 1]
print(winners.head(15))

# 3. Pomocí metody shift() přidej nový sloupec, abys v jednotlivých řádcích měl(a)
# po sobě vítězné strany ve dvou po sobě jdoucích letech.
winners["previous_year_winner"] = winners.groupby(["state"])["party_simplified"].shift(1)
winners = winners.sort_values(["state", "year"])
print(winners.head(15))

# 4. Porovnej, jestli se ve dvou po sobě jdoucích letech změnila vítězná strana.
# Můžeš k tomu použít např. funkci numpy.where() nebo metodu apply().

# pomocí numpy:
# winners["change"] = np.where((winners["year"] != 1976) & (winners["party_simplified"] != winners["previous_year_winner"]), 1, 0)

# pomocí apply:
def winner_change(row):
    if pandas.isnull(row["previous_year_winner"]):
        return 0
    elif row["party_simplified"] == row["previous_year_winner"]:
        return 0
    else:
        return 1
winners["change"] = winners.apply(winner_change, axis=1)
print(winners[winners["state"] == "OHIO"])

# 5. Proveď agregaci podle názvu státu a seřaď státy podle počtu změn vítězných stran.
states_grouped = winners.groupby("state")["change"].sum()
states_grouped = pandas.DataFrame(states_grouped)
states_grouped = states_grouped.sort_values("change", ascending=False)
print(states_grouped.head(20))
# Státy z opačného konce spektra - kde svou volbu nemění:
no_change_states = states_grouped[states_grouped["change"] == 0]
print(no_change_states)

# 6. Vytvoř sloupcový graf s 10 státy, kde došlo k nejčastější změně vítězné strany.
# Jako výšku sloupce nastav počet změn.
# top_10_swinging_states = states_grouped.iloc[:10]
# top_10_swinging_states.plot(kind="bar", color="green", title="Top 10 states with most party changes")
# Alternativně, jako více vypovídající, státy s více než 3 změnami ve sledovaném období
top_swinging_states = states_grouped[states_grouped["change"] >= 3]
top_swinging_states.plot(kind="bar", color="purple", title="States with most party changes")
plt.xlabel("State")
plt.ylabel("Number of changes")
plt.show()

# Pro další část pracuj s tabulkou se dvěma nejúspěšnějšími kandidáty pro každý rok a stát
# (tj. s tabulkou, která oproti té minulé neobsahuje jen vítěze, ale i druhého v pořadí).
top_two_candidates = candidates[candidates["rank"] <= 2].sort_values(["year", "state", "rank"])
# print (top_two_candidates.head())

# 1. Přidej do tabulky sloupec, který obsahuje absolutní rozdíl mezi vítězem a druhým v pořadí.
top_two_candidates["runner_up_votes"] = top_two_candidates.groupby(["state", "year"])["candidatevotes"].shift(-1)
top_two_candidates["abs_diff"] = top_two_candidates["candidatevotes"] - top_two_candidates["runner_up_votes"]
print(top_two_candidates.head(15))

# 2. Přidej sloupec s relativním marginem, tj. rozdílem vyděleným počtem hlasů.
presidents = top_two_candidates.dropna(subset=["runner_up_votes", "abs_diff"])
presidents["relative_margin"] = presidents["abs_diff"] / presidents["totalvotes"]
# print(presidents.head())

# 3. Seřaď tabulku podle velikosti relativního marginu
# a zjisti, kdy a ve kterém státě byl výsledek voleb nejtěsnější.
presidents = presidents.sort_values("relative_margin", ascending=True).reset_index()
# print(presidents.head())
print(f"Nejtěsnější výsledek voleb byl v roce {presidents.loc[0]['year']} ve státě {presidents.loc[0]['state']}.")

# 4. Vytvoř pivot tabulku, která zobrazí pro jednotlivé volební roky, kolik států
# přešlo od Republikánské strany k Demokratické straně, kolik států přešlo od Demokratické strany
# k Republikánské straně a kolik států volilo kandidáta stejné strany.
winners_cleared = winners.drop(winners[winners["year"] == 1976].index).sort_values(["state", "year"])
def swing(row):
    if row["previous_year_winner"] == "DEMOCRAT" and row["party_simplified"] == "REPUBLICAN":
        return "swing to Rep."
    elif row["previous_year_winner"] == "REPUBLICAN" and row["party_simplified"] == "DEMOCRAT":
        return "swing to Dem."
    else:
        return "no swing"
winners_cleared["swing"] = winners_cleared.apply(swing, axis=1)
print(winners_cleared.head(20))
swings_pivot = pandas.pivot_table(data=winners_cleared, values="change", index="year", columns="swing", aggfunc=len)
print(swings_pivot)

