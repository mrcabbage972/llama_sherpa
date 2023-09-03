from app.tasks import docker_task

def test_docker_task():
    result = docker_task('ubuntu', 'echo "hello world"', 0, False, [])
    assert result
