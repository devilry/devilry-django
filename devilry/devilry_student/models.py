# NOTE: Left after removal of UploadedDeliveryFile model to avoid migrations breaking
def uploaded_deliveryfile_path(uploaded_deliveryfile, filename):
    if uploaded_deliveryfile.id is None:
        raise ValueError('Can not add the file to UploadedDeliveryFile before it has an ID.')
    return 'devilry_student/incomplete_deliveries/{id}'.format(id=uploaded_deliveryfile.id)
