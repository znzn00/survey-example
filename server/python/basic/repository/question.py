from abc import ABC, abstractmethod


class QuestionRepository(ABC):
    @abstractmethod
    def getQuestion(id):
        pass
    
    @abstractmethod
    def createQuestion(question):
        pass

    @abstractmethod
    def deleteQuestion(question):
        pass

    @abstractmethod
    def updateQuestion(question):
        pass

    @abstractmethod
    def getQuestions():
        pass