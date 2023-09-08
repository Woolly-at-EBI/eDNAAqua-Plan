#!/usr/bin/env python3
"""Script of geography.py is to geograph.py

___author___ = "woollard@ebi.ac.uk"
___start_date___ = 2023-09-08
__docformat___ = 'reStructuredText'
chmod a+x geography.py
"""


from icecream import ic
import os
import argparse
import re
import sys

class Geography:
  def __init__(self):
      self.build_insdc_lists()


  def is_insdc_country(self, country):
       """
        any eu country or sea
        assumes that you have cleaned the country term!
       """
       if country in self.insdc_full_set:
           return True
       else:
           return False

  def is_insdc_country_in_europe(self, country):
       """
        any european country or seas around europe
        assumes that you have cleaned the country term!
       """
       if country in self.europe_all_set:
           return True
       else:
           return False

  def is_insdc_country_in_eu(self, country):
       """
        any eu country
        assumes that you have cleaned the country term!
       """
       if country in self.eu_set:
           return True
       else:
           return False
  def clean_insdc_country_term(self,country):
      """
      Does some basic cleaning of country terms, is far from exhaustive, but > 80:20
      :param country:
      :return: county
      """
      clean_country = country

      def removeBefore(string, suffix):
          if ':' not in string:
              return string
          else:
              return string[:string.index(suffix) + (len(suffix) -1)]
      def capitalise(string):
          if " " in string:
              list = []
              for sub_str in string.split(' '):
                  if sub_str == 'and':
                      list.append(sub_str)
                  else:
                      list.append(sub_str.capitalize())
              return ' '.join(list)
          else:
              #simpler
              return string.capitalize()

      clean_country = removeBefore(country, ":")
      clean_country = capitalise(clean_country)
      return clean_country


  def build_insdc_lists(self):

     # cmd="curl 'https://www.insdc.org/submitting-standards/country-qualifier-vocabulary/' 2> /dev/null | tr '\n' '@' | sed 's/^.*the-world-factbook\/<\/a><\/p>//;s/<p class.*//;s/<\/ul>.*//' | tr '@' '\n' | sed 's/^[^>]*>//;s/<\/li>$//'"
     insdc_raw = 'Afghanistan,Albania,Algeria,American Samoa,Andorra,Angola,Anguilla,Antarctica,Antigua and Barbuda,Arctic Ocean,Argentina,Armenia,Aruba,Ashmore and Cartier Islands,Atlantic Ocean,Australia,Austria,Azerbaijan,Bahamas,Bahrain,Baltic Sea,Baker Island,Bangladesh,Barbados,Bassas da India,Belarus,Belgium,Belize,Benin,Bermuda,Bhutan,Bolivia,Borneo,Bosnia and Herzegovina,Botswana,Bouvet Island,Brazil,British Virgin Islands,Brunei,Bulgaria,Burkina Faso,Burundi,Cambodia,Cameroon,Canada,Cape Verde,Cayman Islands,Central African Republic,Chad,Chile,China,Christmas Island,Clipperton Island,Cocos Islands,Colombia,Comoros,Cook Islands,Coral Sea Islands,Costa Rica,Cote d&#8217;Ivoire,Croatia,Cuba,Curacao,Cyprus,Czech Republic,Democratic Republic of the Congo,Denmark,Djibouti,Dominica,Dominican Republic,Ecuador,Egypt,El Salvador,Equatorial Guinea,Eritrea,Estonia,Eswatini,Ethiopia,Europa Island,Falkland Islands (Islas Malvinas),Faroe Islands,Fiji,Finland,France,French Guiana,French Polynesia,French Southern and Antarctic Lands,Gabon,Gambia,Gaza Strip,Georgia,Germany,Ghana,Gibraltar,Glorioso Islands,Greece,Greenland,Grenada,Guadeloupe,Guam,Guatemala,Guernsey,Guinea,Guinea-Bissau,Guyana,Haiti,Heard Island and McDonald Islands,Honduras,Hong Kong,Howland Island,Hungary,Iceland,India,Indian Ocean,Indonesia,Iran,Iraq,Ireland,Isle of Man,Israel,Italy,Jamaica,Jan Mayen,Japan,Jarvis Island,Jersey,Johnston Atoll,Jordan,Juan de Nova Island,Kazakhstan,Kenya,Kerguelen Archipelago,Kingman Reef,Kiribati,Kosovo,Kuwait,Kyrgyzstan,Laos,Latvia,Lebanon,Lesotho,Liberia,Libya,Liechtenstein,Line Islands,Lithuania,Luxembourg,Macau,Madagascar,Malawi,Malaysia,Maldives,Mali,Malta,Marshall Islands,Martinique,Mauritania,Mauritius,Mayotte,Mediterranean Sea,Mexico,Micronesia, Federated States of,Midway Islands,Moldova,Monaco,Mongolia,Montenegro,Montserrat,Morocco,Mozambique,Myanmar,Namibia,Nauru,Navassa Island,Nepal,Netherlands,New Caledonia,New Zealand,Nicaragua,Niger,Nigeria,Niue,Norfolk Island,North Korea,North Macedonia,North Sea,Northern Mariana Islands,Norway,Oman,Pacific Ocean,Pakistan,Palau,Palmyra Atoll,Panama,Papua New Guinea,Paracel Islands,Paraguay,Peru,Philippines,Pitcairn Islands,Poland,Portugal,Puerto Rico,Qatar,Republic of the Congo,Reunion,Romania,Ross Sea,Russia,Rwanda,Saint Barthelemy,Saint Helena,Saint Kitts and Nevis,Saint Lucia,Saint Martin,Saint Pierre and Miquelon,Saint Vincent and the Grenadines,Samoa,San Marino,Sao Tome and Principe,Saudi Arabia,Senegal,Serbia,Seychelles,Sierra Leone,Singapore,Sint Maarten,Slovakia,Slovenia,Solomon Islands,Somalia,South Africa,South Georgia and the South Sandwich Islands,South Korea,South Sudan,Southern Ocean,Spain,Spratly Islands,Sri Lanka,State of Palestine,Sudan,Suriname,Svalbard,Sweden,Switzerland,Syria,Taiwan,Tajikistan,Tanzania,Tasman Sea,Thailand,Timor-Leste,Togo,Tokelau,Tonga,Trinidad and Tobago,Tromelin Island,Tunisia,Turkey,Turkmenistan,Turks and Caicos Islands,Tuvalu,USA,Uganda,Ukraine,United Arab Emirates,United Kingdom,Uruguay,Uzbekistan,Vanuatu,Venezuela,Viet Nam,Virgin Islands,Wake Island,Wallis and Futuna,West Bank,Western Sahara,Yemen,Zambia,Zimbabwe'
     insdc_full_list = insdc_raw.split(',')
     self.insdc_full_set = set(insdc_full_list)
     #print(self.insdc_full_list)

     #https://www.gov.uk/eu-eea
     eu_raw="Austria, Belgium, Bulgaria, Croatia, Republic of Cyprus, Czech Republic, Denmark, Estonia, Finland, France, Germany, Greece, Hungary, Ireland, Italy, Latvia, Lithuania, Luxembourg, Malta, Netherlands, Poland, Portugal, Romania, Slovakia, Slovenia, Spain, Sweden"
     eu_list=eu_raw.split(', ')
     # print(eu_list)


     noneu_euro_raw="Iceland,Liechtenstein,Norway,Switzerland,United Kingdom,Albania,Belarus,Gibraltar,Jersey,Montenegro,San Marino,Svalbard,Moldova,Isle of Man,Monaco,Cyprus,Bosnia and Herzegovina,North Macedonia,Serbia,Andorra,Russia,Guernsey,"
     noneu_euro_list=noneu_euro_raw.split(',')
     europe_list = sorted(noneu_euro_list + eu_list)
     not_europe_set = set()

     ocean_sea_set = set()
     country_set = set()
     for term in sorted(insdc_full_list):
        if re.search(r"Sea|Ocean", term):
             ocean_sea_set.add(term)
        else:
            country_set.add(term)
     #print("++++++++++++++++++++++++++++++++++++++++++++")
     for country in sorted(country_set):
        if country not in europe_list:
            #print(country)
            not_europe_set.add(country)
     self.not_europe_set = not_europe_set
     self.europe_country_set = set(europe_list)
     european_sea_list = ['Mediterranean Sea', 'North Sea', 'Baltic Sea']
     self.europe_all_set = self.europe_country_set.union(set(european_sea_list))
     self.eu_set = set(eu_list)
     self.none_eu_europe_set = self.europe_all_set.difference(self.eu_set)
     self.ocean_sea_set = ocean_sea_set
     self.country_set = country_set


  def print_summary(self):

      out_string = ""
      out_string += f"insdc_full_set:\t{len(self.insdc_full_set)}\n"
      out_string += f"country_set:\t{len(self.country_set)}\n"
      out_string += f"ocean_sea_set:\t{len(self.ocean_sea_set)}\n"
      out_string += f"europe_country_set:\t{len(self.europe_country_set)}\n"
      out_string += f"not_europe_set:\t{len(self.not_europe_set)}\n"
      out_string += f"europe_all_set:\t{len(self.europe_all_set)}\n"
      out_string += f"eu_set:\t{len(self.eu_set)}\n"
      out_string += f"none_eu_europe_set:\t{len(self.none_eu_europe_set)}\n"

      return out_string

def main():
    geography = Geography()
    print(geography.print_summary())

    for test_term in ['France','FRANCE','France:Paris','UK','Australia', 'North Sea', "North sea", 'Antigua and Barbuda']:
          ic(test_term)
          clean_term = geography.clean_insdc_country_term(test_term)
          ic(geography.is_insdc_country_in_europe(clean_term))
          ic(geography.is_insdc_country_in_eu(clean_term))
          ic(geography.is_insdc_country(clean_term))
          ic("+++++++++++++++++++++++++++++++++++")

if __name__ == '__main__':
    ic()
    main()
