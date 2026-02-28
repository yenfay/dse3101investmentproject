dse3101 project

DSE3101INVESTMENTPROJECT/
├── Backend/
│   ├── download/
│   ├── transform/
│   │   ├── __init__.py
│   │   ├── etl_pipeline.py        # process all the zip file in 13F_zip_files into parquet file in 13F_clean_files
│   │   ├── process_single_zip.py  # clean one form13f zip file
│   ├── query_functions/           # query functions (tbc)
│   │   ├── __init__.py
│   │   ├── query_parquet.py       # query functions for query parquet in future (tbc)
│   └── utils/
├── Datasets/
│   │   ├── 13F_clean_files/       # contains all the cleaned form13f parquet files by quarters
│   │   ├── 13F_zip_files/         # contains raw form13f zip files    
├── Frontend/
├── temp/temp_extract/
├── venv                           # to activate virtual environment
├── requirements.txt
├── .gitattributes                 # to upload all parquet files in 13F_clean_files into Git LFS
├── .gitignore
└── README.md