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

def get_citation_counts_for_paper(bibcode):

    query = ads.SearchQuery(q='citations(bibcode:{0})'.format(bibcode),
                            database='astronomy', property='refereed',
                            rows=2000, max_pages=2000)

    query.execute()

    paper_years = [int(art.year) for art in query.articles]

    counts = []

    for yr in sorted(set(paper_years)):
        counts.append(paper_years.count(yr))

    return sorted(set(paper_years)), counts

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


    for lang in ('Python', 'Astropy', 'IDL', 'Fortran', 'Matlab', 'CASA',
                 'AIPS', 'sunpy', 'astropy affiliated', 'astroquery', 'IRAF',
                 'gildas', 'virtual observatory', 'erdas', 'khoros', 'pyraf',
                 'starlink', 'gipsy', 'karma',
                ):
        if lang not in years:
            years[lang], values[lang] = get_numbers(lang)
        # filter out zero-years
        years[lang] = years[lang][values[lang]>0]
        values[lang] = values[lang][values[lang]>0]

    if 'total' not in years:
        years['total'], values['total'] = get_total()


    if 'iraf_plus_pyraf' not in locals():
        iraf_plus_pyraf = 'Done'
        for ii,yr in enumerate(years['IRAF']):
            inds = years['pyraf'] == yr
            if any(inds):
                values['IRAF'][ii] += values['pyraf'][inds]

    if 'astropy2013' not in years:
        # astropy 2013 paper
        astropy2013ppr = get_citation_counts_for_paper('2013A&A...558A..33A')
        years['astropy2013'] = np.array(astropy2013ppr[0])
        values['astropy2013'] = np.array(astropy2013ppr[1])

    if 'astropy2018' not in years:
        # astropy 2018 paper
        astropy2018ppr = get_citation_counts_for_paper('2018AJ....156..123A')
        years['astropy2018'] = np.array(astropy2018ppr[0])
        values['astropy2018'] = np.array(astropy2018ppr[1])


    if 'yt' not in years:
        # yt 2011 paper
        ytppr = get_citation_counts_for_paper('2011ApJS..192....9T')
        years['yt'] = np.array(ytppr[0])
        values['yt'] = np.array(ytppr[1])


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

    ax.plot(years['IRAF'], get_ratio('IRAF', 'total'), '.-', label='IRAF+pyraf')
    #ax.plot(years['pyraf'], get_ratio('pyraf', 'total'), '.-', label='pyraf')
    ax.plot(years['CASA'], get_ratio('CASA', 'total'), '.-', label='CASA')
    ax.plot(years['AIPS'], get_ratio('AIPS', 'total'), '.-', label='AIPS')
    ax.plot(years['gildas'], get_ratio('gildas', 'total'), '.-', label='gildas')
    ax.plot(years['virtual observatory'], get_ratio('virtual observatory', 'total'), '.-', label='virtual observatory')
    ax.legend(fontsize=8, loc=2)
    plt.savefig('hockey_stick_graph_normalized_all.png', dpi=150)

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
    #ax.plot(years['astropy affiliated'], values['astropy affiliated'], '.-', label='astropy affiliated', alpha=0.5)
    #ax.plot(years['astroquery'], values['astroquery'], '.-', label='astroquery', alpha=0.5)
    ax.plot(years['IRAF'], values['IRAF'], '.-', label='IRAF+pyraf', alpha=0.5)
    #ax.plot(years['pyraf'], values['pyraf'], '.-', label='pyraf', alpha=0.5)
    #ax.plot(years['astropy2013'], values['astropy2013'], '.-', label='astropy2013', alpha=0.5)
    #ax.plot(years['astropy2018'], values['astropy2018'], '.-', label='astropy2018', alpha=0.5)
    ax.plot(years['yt'], values['yt'], '.--', label='yt', alpha=0.5)
    ax.plot(years['gildas'], values['gildas'], '.--', label='gildas', alpha=0.5)
    ax.plot(years['virtual observatory'], values['virtual observatory'], '.--', label='virtual observatory')
    #ax.plot(years['karma'], values['karma'], '.--', label='karma', alpha=0.5)
    ax.plot(years['starlink'], values['starlink'], '.--', label='starlink', alpha=0.5)
    #ax.plot(years['gipsy'], values['gipsy'], '.--', label='gipsy', alpha=0.5)
    #ax.plot(years['sunpy'], values['sunpy'], '.-', label='sunpy', alpha=0.5)

    ax.legend(fontsize=8, loc=2)
    # can't show this year b/c it isn't normalized
    ax.set_xlim(1970, thisyear)
    ax.xaxis.get_major_formatter().set_useOffset(False)
    ax.set_ylabel("Number of papers")
    ax.set_xlabel("Year")
    plt.savefig('hockey_stick_graph_withCASAandAIPS.png', dpi=150)
    ax.set_xlim(2000, thisyear)
    plt.savefig('hockey_stick_graph_withCASAandAIPS_since2000.png', dpi=150)
    ax.set_xlim(2008, thisyear)
    plt.savefig('hockey_stick_graph_withCASAandAIPS_since2008.png', dpi=150)


    fig = plt.figure(num=4, figsize=(10,6))
    fig.clf()
    ax = fig.add_subplot(1,1,1)

    ax.set_title("Fraction of python papers mentioning astropy", size=10)
    fracyrs, astropy_fraction = get_ratio('Astropy', 'Python', return_years=True)
    ax.plot(fracyrs[fracyrs>2000], astropy_fraction[fracyrs>2000], '.-',
            label='Astropy/Python')
    fracyrs2, astropycite_fraction = get_ratio('astropy2013', 'Astropy', return_years=True)
    ax.plot(fracyrs2[fracyrs2>2000], astropycite_fraction[fracyrs2>2000], '.-',
            label='Astropy 2013/Astropy')
    plt.legend(loc='best')

    #ax.legend(fontsize=8, loc=2)
    # can't show this year b/c it isn't normalized
    ax.set_xlim(1970, thisyear)
    #ax.set_ylim(0, astropy_fraction[np.isfinite(astropy_fraction)].max()+0.05)
    ax.xaxis.get_major_formatter().set_useOffset(False)
    ax.set_ylabel("Fraction of papers")
    ax.set_xlabel("Year")
    ax.set_xlim(2012, thisyear)
    plt.savefig('hockey_stick_graph_astropyfraction_since2012.png', dpi=150)
