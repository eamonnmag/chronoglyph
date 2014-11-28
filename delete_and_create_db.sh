rm -rf ChronoGlyph_Web/migrations
rm -rf *.db
python manage.py schemamigration ChronoGlyph_Web --initial
python manage.py syncdb
python manage.py migrate ChronoGlyph_Web