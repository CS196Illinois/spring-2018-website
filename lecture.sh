if [[ $1 = --help ]]
  then
    echo "---------------------------"
    echo "-   196 lecture signins   -"
    echo "-  @duke vijitbenjaronk   -"
    echo "---------------------------\n"
    echo "./lecture.sh open-session    opens a new lecture session"
    echo "./lecture.sh close-session   closes the current lecture session"
    echo "./lecture.sh --help          opens the current help dialog"
    echo "./lecture.sh backup          updates the server backup"
  elif [[ $1 = open-session ]]
    then
      curl http://cs196.cs.illinois.edu/opensession
  elif [[ $1 = close-session ]]
    then
      curl http://cs196.cs.illinois.edu/closesession
  elif [[ $1 = backup ]]
    then
      curl http://cs196.cs.illinois.edu/backup
fi

