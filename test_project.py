from project import verify_arguments, process_block_images, generate_materials_table
import pytest

def test_verify_arguments():

    with pytest.raises(SystemExit):
        verify_arguments()


def test_process_block_images():
    dict = {}
    assert process_block_images(dict) == None


def test_generate_materials_table():
    materials_dict = {}
    assert generate_materials_table(materials_dict) == None
