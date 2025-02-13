import docker


class Docker:
    def __init__(
        self,
        image: str,
        command=None,
        environment=None,
        volumes=None,
        auto_remove: bool =True
    ):
        """
        Initialize the Docker task runner.

        :param image: Docker image to use.
        :param command: Command to run inside the container.
        :param environment: Dictionary of environment variables.
        :param volumes: Dictionary of volume mappings (host_path: container_path).
        :param auto_remove: Whether to remove the container after execution.
        """
        self.image: str = image
        self.command = command
        self.environment = environment or {}
        self.volumes = volumes or {}
        self.auto_remove = auto_remove
        self.client = docker.from_env()

    def run(self):
        """
        Run the Docker container and stream logs.
        """
        try:
            print(f"Pulling Docker image: {self.image}")
            self.client.images.pull(self.image)

            print(f"Running container with image: {self.image}")
            container = self.client.containers.run(
                self.image,
                command=self.command,
                environment=self.environment,
                volumes={
                    host: {'bind': container, 'mode': 'rw'}
                    for host, container in self.volumes.items()
                },
                auto_remove=self.auto_remove,
                detach=True,
            )

            for line in container.logs(stream=True):
                print(line.strip().decode())

            container.wait()  # Ensure container completes execution
            print("Docker task execution completed.")
        except Exception as e:
            print(f"Error running Docker task: {e}")
            raise


if __name__ == "__main__":
    task = Docker(
        image="python:3.9",
        command="python -c 'print(\"Hello from Docker!\")'",
        environment={"MY_ENV_VAR": "value"},
        volumes={"/host/path": "/container/path"}
    )
    task.run()
