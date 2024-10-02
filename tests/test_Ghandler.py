"""
Tests google handler

Use before testing:
$env:PYTHONPATH = "C:\path\to\root"
"""

import googleHandler
import doc_config

doc1id = "11MsoEDRaTgsTmxQUIaRRq66siEpG3gSd9fhT0Aaawmg"
doc2id = "1CuSugnNmvt39w1YpTdA3lCLyk7KCOim9kOC9uKQsXzY"
doc3id = "1XxDyhaLq2UE84coyKYLvgyDKrgZE9kCocuK-qdBzTYk"

testing_folder = "1lWypBionbXiC0O4mB4YzqJ4NMaq6_xql"

def test_file_exists():
    assert googleHandler.file_exists("Testing 1: Published", testing_folder) == True
    assert googleHandler.file_exists("nonexistent file", testing_folder) == False

def test_get_id_by_name():
    assert googleHandler.get_file_id_by_name("Testing 2: Unpublished", testing_folder) == "1CuSugnNmvt39w1YpTdA3lCLyk7KCOim9kOC9uKQsXzY"
    assert googleHandler.get_file_id_by_name("nonexistent_file", testing_folder) == None

def test_get_file_link():
    assert googleHandler.get_file_link(testing_folder, "Testing 3: Unpublished") == "https://docs.google.com/document/d/1XxDyhaLq2UE84coyKYLvgyDKrgZE9kCocuK-qdBzTYk/edit?usp=drive_link"
    assert googleHandler.get_file_link(testing_folder, "nonexistent_file") == None

def test_get_folder_from_docname():
    assert googleHandler.get_folder_from_docname("BM Transparency Report: Fall Quarter 2024") == doc_config.folder_id or googleHandler.get_folder_from_docname("BM Transparency Report: Fall Quarter 2024") == doc_config.share_folder_id
    assert googleHandler.get_folder_from_docname("nonexistent_file") == None

def test_check_string_in_doc():
    assert googleHandler.check_string_in_doc(doc1id, "Published") ==  True
    assert googleHandler.check_string_in_doc(doc2id, "Unpublished") == True
    assert googleHandler.check_string_in_doc(doc3id, "Published") == False
    assert googleHandler.check_string_in_doc(doc3id, "Cats") == False