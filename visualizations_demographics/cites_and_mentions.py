from matplotlib import pyplot as plt

from datetime import datetime
import ads
import numpy as np

thisyear = datetime.today().year

def get_numbers(language):
    print("Getting {0} #'s".format(language))

    years = np.arange(1970, thisyear+1)
    values = []

    for year in years:
        print("Getting {0}".format(year))
        query = ads.SearchQuery(full=language, database='astronomy', property='refereed',
                                year="{0}".format(year),
                                fl=['year'], rows=100, max_pages=1000)
        query.execute()
        values.append(query.response.numFound)

    return years, np.array(values, dtype=float)

def get_total():
    print("Getting total #'s")
    years = np.arange(1970, thisyear+1)
    values = []

    for year in years:
        print("Getting {0}".format(year))
        result = ads.SearchQuery(database='astronomy', year="{0}".format(year),
                                 property='refereed', fl=['year'], rows=1,
                                 max_pages=1)
        result.execute()
        values.append(result.response.numFound)

    return years, np.array(values)

if __name__ == "__main__":
    if 'years' not in locals():
        # "cache" the queries if running multiple times interactively
        years = {}
        values = {}


    for lang in ('Python', 'Astropy', 'IDL', 'Fortran', 'Matlab', 'CASA', 'AIPS', 'sunpy', 'astropy affiliated', 'astroquery'):
        if lang not in years:
            years[lang], values[lang] = get_numbers(lang)
        # filter out zero-years
        years[lang] = years[lang][values[lang]>0]
        values[lang] = values[lang][values[lang]>0]

    if 'total' not in years:
        years['total'], values['total'] = get_total()


    plt.rc('font', family='Source Sans Pro')

    fig = plt.figure(num=1, figsize=(10,6))
    fig.clf()
    ax = fig.add_subplot(1,1,1)

    ax.set_title("Full text mentions of programming languages in Astronomy papers", size=10)
    ax.plot(years['Python'], values['Python'], '.-', label='Python')
    ax.plot(years['IDL'], values['IDL'], '.-', label='IDL')
    ax.plot(years['Fortran'], values['Fortran'], '.-', label='Fortran')
    ax.plot(years['Matlab'], values['Matlab'], '.-', label='Matlab')
    ax.plot(years['Astropy'], values['Astropy'], '.-', label='Astropy')

    ax.legend(fontsize=8, loc=2)
    # can't show this year b/c it isn't normalized
    ax.set_xlim(1970, thisyear)
    ax.xaxis.get_major_formatter().set_useOffset(False)
    ax.set_ylabel("Number of papers")
    ax.set_xlabel("Year")
    plt.savefig('hockey_stick_graph.png', dpi=150)



    fig = plt.figure(num=2, figsize=(10,6))
    fig.clf()
    ax = fig.add_subplot(1,1,1)

    def get_ratio(kw1, kw2, return_years=False):
        yr1, val1 = years[kw1], values[kw1]
        yr2, val2 = years[kw2], values[kw2]
        ryears = []
        ratio = []
        for yr, num in zip(yr1, val1):
            try:
                ind = list(yr2).index(yr)
                den = val2[ind]
                ratio.append(num/den)
                ryears.append(yr)
            except ValueError as ex:
                print(ex)

        #assert len(yr1) == len(ratio)

        if return_years:
            return np.array(ryears), np.array(ratio)
        else:
            return np.array(ratio)

    ax.set_title("Fraction of papers mentioning each language", size=10)
    ax.plot(years['Python'], get_ratio('Python', 'total'), '.-', label='Python')
    ax.plot(years['IDL'], get_ratio('IDL', 'total'), '.-', label='IDL')
    ax.plot(years['Fortran'], get_ratio('Fortran', 'total'), '.-', label='Fortran')
    ax.plot(years['Matlab'], get_ratio('Matlab', 'total'), '.-', label='Matlab')
    ax.plot(years['Astropy'], get_ratio('Astropy', 'total'), '.-', label='Astropy')

    ax.legend(fontsize=8, loc=2)
    ax.set_xlim(1970, thisyear)
    ax.xaxis.get_major_formatter().set_useOffset(False)
    ax.set_ylabel("Fraction of all astronomy papers")
    ax.set_xlabel("Year")
    plt.savefig('hockey_stick_graph_normalized.png', dpi=150)


    fig = plt.figure(num=3, figsize=(10,6))
    fig.clf()
    ax = fig.add_subplot(1,1,1)

    ax.set_title("Full text mentions of programming languages in Astronomy papers", size=10)
    ax.plot(years['Python'], values['Python'], '.-', label='Python')
    ax.plot(years['IDL'], values['IDL'], '.-', label='IDL')
    ax.plot(years['Fortran'], values['Fortran'], '.-', label='Fortran')
    ax.plot(years['Matlab'], values['Matlab'], '.-', label='Matlab')
    ax.plot(years['Astropy'], values['Astropy'], '.-', label='Astropy')
    ax.plot(years['CASA'], values['CASA'], '.-', label='CASA')
    ax.plot(years['AIPS'], values['AIPS'], '.-', label='AIPS')
    ax.plot(years['astropy affiliated'], values['astropy affiliated'], '.-', label='astropy affiliated', alpha=0.5)
    ax.plot(years['astroquery'], values['astroquery'], '.-', label='astroquery', alpha=0.5)

    ax.legend(fontsize=8, loc=2)
    # can't show this year b/c it isn't normalized
    ax.set_xlim(1970, thisyear)
    ax.xaxis.get_major_formatter().set_useOffset(False)
    ax.set_ylabel("Number of papers")
    ax.set_xlabel("Year")
    plt.savefig('hockey_stick_graph_withCASAandAIPS.png', dpi=150)
    ax.set_xlim(2000, thisyear)
    plt.savefig('hockey_stick_graph_withCASAandAIPS_since2000.png', dpi=150)


    fig = plt.figure(num=4, figsize=(10,6))
    fig.clf()
    ax = fig.add_subplot(1,1,1)

    ax.set_title("Fraction of python papers mentioning astropy", size=10)
    fracyrs, astropy_fraction = get_ratio('Astropy', 'Python', return_years=True)
    ax.plot(fracyrs[fracyrs>2000], astropy_fraction[fracyrs>2000], '.-',
            label='Astropy/Python')

    #ax.legend(fontsize=8, loc=2)
    # can't show this year b/c it isn't normalized
    ax.set_xlim(1970, thisyear)
    #ax.set_ylim(0, astropy_fraction[np.isfinite(astropy_fraction)].max()+0.05)
    ax.xaxis.get_major_formatter().set_useOffset(False)
    ax.set_ylabel("Fraction of papers")
    ax.set_xlabel("Year")
    ax.set_xlim(2000, thisyear)
    plt.savefig('hockey_stick_graph_astropyfraction_since2000.png', dpi=150)


