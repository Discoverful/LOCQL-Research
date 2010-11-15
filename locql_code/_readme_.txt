./get_en_questions.py
./get_local_questions.py > data/get_local_questions.log
cut -f 3 data/get_local_questions.log > data/place_names.txt
touch data/local_geoplaces.txt
./get_local_geoplaces.py
./get_local_properties.py
./get_place_categories.py 'london' > data/place_categories_london.txt
./get_place_categories.py 'san francisco' > data/place_categories_san-francisco.txt
./get_place_categories.py 'seattle' > data/place_categories_seattle.txt
./get_place_questions.py 'london' | sort > data/place_questions_london.txt
./get_place_questions.py 'san francisco' | sort > data/place_questions_san-francisco.txt
./get_place_questions.py 'seattle' | sort > data/place_questions_seattle.txt
