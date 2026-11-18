# Parses a compose.yaml port mapping the way Compose reads it, so the ports control compares
# the running container with what Compose would actually have published.
module ComposePorts
  VARIABLE = /\$\{([A-Za-z_][A-Za-z0-9_]*)(?::-([^}]*))?\}/

  # Expands ${VAR} and ${VAR:-default}: the variable when set and non-empty, otherwise the
  # default (empty when there is none), as Compose does. The environment must be the one the
  # stack was started with, so pass the same variables to the conformance run.
  def self.expand(text, env)
    text.gsub(VARIABLE) do
      value = env[Regexp.last_match(1)]
      value.nil? || value.empty? ? Regexp.last_match(2).to_s : value
    end
  end

  # Returns [host_ip, host_port, container_port]; the host IP is 0.0.0.0 when unspecified.
  def self.parse(mapping, env = ENV)
    parts = expand(mapping.to_s, env).split(':')
    container_port = parts.pop
    host_port = parts.pop
    host_ip = parts.empty? ? '0.0.0.0' : parts.pop
    [host_ip, host_port, container_port]
  end
end
