HEUDICONV_CMD_TEMPLATE = """
heudiconv --bids notop -c dcm2niix -g all -f {heuristic} --files '{dicom_directory}'/*/*.dcm -o {output_directory} -ss {session_id} -s {subject_id}
"""  # noqa: E501
