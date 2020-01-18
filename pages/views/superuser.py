def dataset(request):
    template = loader.get_template('{}/dataset.html'.format(ADMIN_DIR))

    # get all VotingData ids that are not allocated to any user
    ids = [i.id for i in VotingData.objects.all()]
    exclude_ids = [i.task.id for i in Assignment.objects.all()]
    for exclude_id in exclude_ids:
        if exclude_id in ids:
            ids.remove(exclude_id)

    # get all VotingData objects and combine them with their respective choices
    voting_data = []
    for id in ids:
        voting_data.append(VotingData.objects.get(question_id=id))
    for data in voting_data:
        data.answers = Choice.objects.filter(data_id=data.question_id)

    # calculate num of data of each type
    groups = CustomGroup.objects.all()
    num_data = {}
    num_data["all"] = FinalizedData.objects.all().count()
    for group in groups:
        num_data[group.name] = FinalizedData.objects.all().filter(group=group).count()

    context = {
        'title': 'Data Set',
        'num_data': num_data,
        'data': voting_data,
        'types': groups,
        'login_user': request.user,
    }
    return HttpResponse(template.render(context=context))