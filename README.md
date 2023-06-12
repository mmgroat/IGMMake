# IGMMake
IGMMake: GedCom to Web program written in PERL

I'm abandoning IGM/IGMMake in favor of a new project called GIMM (GedCom in Memory Method) (previously printVeryLargeTextPedigrees) that puts a local gedcom file into memory before serving web pages, thus elavating the need to make several disk requests each time a page is called. A 50,000 person pedigree chart, which use to take 3 minutes to load on IGM, takes less than a second on GIMM (printVeryLargeTextPedigrees).

