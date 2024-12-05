from rest_framework import serializers

class TaskSerializer(serializers.Serializer):
    name = serializers.CharField()

class ListOfTasksSerializer(serializers.Serializer):
    tasks = TaskSerializer