import os
import re
import gradio as gr
from easygui import msgbox, boolbox
from .common_gui import get_folder_path

# def select_folder():
#     # Open a file dialog to select a directory
#     folder = filedialog.askdirectory()

#     # Update the GUI to display the selected folder
#     selected_folder_label.config(text=folder)


def dataset_balancing(concept_repeats, folder, insecure):

    if concept_repeats <= 0:
        # Display an error message if the total number of repeats is not a valid integer
        msgbox('Please enter a valid integer for the total number of repeats.')
        return

    concept_repeats = int(concept_repeats)

    # Check if folder exist
    if folder == '' or not os.path.isdir(folder):
        msgbox('Please enter a valid folder for balancing.')
        return

    pattern = re.compile(r'^\d+_.+$')

    # Iterate over the subdirectories in the selected folder
    for subdir in os.listdir(folder):
        if pattern.match(subdir) or insecure:
            # Calculate the number of repeats for the current subdirectory
            # Get a list of all the files in the folder
            files = os.listdir(os.path.join(folder, subdir))

            # Filter the list to include only image files
            image_files = [
                f
                for f in files
                if f.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))
            ]

            # Count the number of image files
            images = len(image_files)

            if images == 0:
                print(
                    f'No images of type .jpg, .jpeg, .png, .gif, .webp were found in {os.listdir(os.path.join(folder, subdir))}'
                )

            if match := re.match(r'^\{(\d+\.?\d*)\}', subdir):
                # Multiply the repeats value by the number inside the braces
                repeats = (
                    max(
                        1,
                        round(
                            concept_repeats / images * float(match.group(1))
                        ),
                    )
                    if images != 0
                    else 0
                )
                subdir = subdir[match.end() :]
            elif images != 0:
                repeats = max(1, round(concept_repeats / images))
            else:
                repeats = 0

            if match := re.match(r'^\d+_', subdir):
                # Replace the existing number with the new number
                old_name = os.path.join(folder, subdir)
                new_name = os.path.join(
                    folder, f'{repeats}_{subdir[match.end():]}'
                )
            else:
                # Add the new number at the beginning of the name
                old_name = os.path.join(folder, subdir)
                new_name = os.path.join(folder, f'{repeats}_{subdir}')

            os.rename(old_name, new_name)
        else:
            print(
                f'Skipping folder {subdir} because it does not match kohya_ss expected syntax...'
            )

    msgbox('Dataset balancing completed...')


def warning(insecure):
    if insecure:
        return bool(
            boolbox(
                f'WARNING!!! You have asked to rename non kohya_ss <num>_<text> folders...\n\nAre you sure you want to do that?',
                choices=('Yes, I like danger', 'No, get me out of here'),
            )
        )


def gradio_dataset_balancing_tab(headless=False):
    with gr.Tab('Dreambooth/LoRA Dataset balancing'):
        gr.Markdown(
            'This utility will ensure that each concept folder in the dataset folder is used equally during the training process of the dreambooth machine learning model, regardless of the number of images in each folder. It will do this by renaming the concept folders to indicate the number of times they should be repeated during training.'
        )
        gr.Markdown(
            'WARNING! The use of this utility on the wrong folder can lead to unexpected folder renaming!!!'
        )
        with gr.Row():
            select_dataset_folder_input = gr.Textbox(
                label='Dataset folder',
                placeholder='Folder containing the concepts folders to balance...',
                interactive=True,
            )

            select_dataset_folder_button = gr.Button(
                '📂', elem_id='open_folder_small', visible=(not headless)
            )
            select_dataset_folder_button.click(
                get_folder_path,
                outputs=select_dataset_folder_input,
                show_progress=False,
            )

            total_repeats_number = gr.Number(
                value=1000,
                interactive=True,
                label='Training steps per concept per epoch',
            )
        with gr.Accordion('Advanced options', open=False):
            insecure = gr.Checkbox(
                value=False,
                label='DANGER!!! -- Insecure folder renaming -- DANGER!!!',
            )
            insecure.change(warning, inputs=insecure, outputs=insecure)
        balance_button = gr.Button('Balance dataset')
        balance_button.click(
            dataset_balancing,
            inputs=[
                total_repeats_number,
                select_dataset_folder_input,
                insecure,
            ],
            show_progress=False,
        )
