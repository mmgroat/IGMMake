# IGMMake
IGM (Indexed GEDCOM Method): GedCom to Web program written in PERL

I'm abandoning this project, IGM/IGMMake, in favor of a new project called GIMM (GedCom in Memory Method), previously printVeryLargeTextPedigrees, that puts a local GEDCOM file into memory before serving web pages, thus elavating the need to make several disk requests/seeks each time a page is called. 

Each project handles 50,000 plus person pedigree charts, but GIMMWebservice is optimized to run faster, since everything is loaded into memory. If you don't have the availalbe RAM, and don't mind the time to render pages, IGM might still be of use.

