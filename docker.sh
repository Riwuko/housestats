#!/usr/bin/env bash

help=$(cat <<-EOF
Usage: $0 [options]

    -h / --help                     Show this help

Containers:
    up                              run environment (will be build if does not exist)
    build                           build or force rebuild environment
    destroy                         stop and remove containers, networks, images, and volumes
    purge                           purge unused containers and images
    migrate                         migrate and upgrade postgres database
    postgres                        run psql commands in the postgres container

EOF
)

case "$1" in

    up)
        docker-compose up
        ;;
    build)
        docker-compose build
        ;;
    destroy)
        docker-compose down -v --rmi local
        ;;
    debug)
        docker-compose run -p'8080:8080' -e 'DEBUG=TRUE' --rm web python app.py
        ;;
    purge)
        docker rm $(docker ps -aq)
        docker images | grep none | awk '{print "docker rmi " $3;}' | sh
        ;;
    migrate)
        docker-compose run web python manage.py flask db migrate
        docker-compose run web python manage.py flask db upgrade
        ;;
    postgres)
        docker-compose exec postgres psql -U postgres
        ;;


    --help|-h)
        echo "$help"
        ;;
    *)
        echo -e "Unknown parameter $1!"
        echo "$help"
        ;;
esac
