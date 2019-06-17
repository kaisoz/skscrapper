# SkScrapper

SkScrapper is a very simple web scrapper for the [SlimmerKopen](http://www.slimmerkopen.nl) website. SlimmerKopen is a Dutch social housing website that sells houses in a very appealing selling conditions. Given its popularity, the houses are offered in a sort of a lottery system: the earlier you click on an offer, the more probabilities you have to be one of the first viewers.

SkScrapper uses the Selenium framework to automatically refresh the offers list and sign up in on new offers.

## Prerequisites

- Install the Chrome browser.
- Download and unpack the [Chromedriver](http://chromedriver.chromium.org/downloads) for your Chrome version.
- Install requirements:
```bash
pip install -r requirements.txt
```

## Using SkScrapper

1. Register in the [SlimmerKopen](http://www.slimmerkopen.nl) website.
1. Create alerts for houses that match your criteria.
1. Run the scrapper:

```bash
python skscrapper.py -u <slimmerkopen user> -p <slimmerkopen pass> -c <path to chromedriver binary>
```

SkScrapper will check the offers page each second and will automatically sign up in all new offers that match your criteria. For each registration, it will create an entry in a local sqlite database called offers.db with information about the offer.
