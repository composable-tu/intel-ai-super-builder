pub enum HealthCheckStatus {
    Ready,
    LlmModelNotFound,
    EmbeddingModelNotFound,
    Downloading,
    Healthy,
    Unhealthy,
    NotReady,
    Unknown,
}

impl HealthCheckStatus {
    pub fn from_message(message: &str) -> Self {
        match message {
            "ready" => HealthCheckStatus::Ready,
            "llmmodelnotfound" => HealthCheckStatus::LlmModelNotFound,
            "embeddingmodelnotfound" => HealthCheckStatus::EmbeddingModelNotFound,
            "downloading" => HealthCheckStatus::Downloading,
            "healthy" => HealthCheckStatus::Healthy,
            "notready" => HealthCheckStatus::NotReady,
            "unhealthy" => HealthCheckStatus::Unhealthy,
            _ => HealthCheckStatus::Unknown,
        }
    }
}
