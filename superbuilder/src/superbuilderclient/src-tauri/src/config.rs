use serde::Deserialize;
use std::{fs, path::PathBuf};



#[derive(Deserialize)]
pub struct Config {
    pub grpc: GrpcConfig,
}

#[derive(Deserialize)]
pub struct GrpcConfig {
    pub host: Option<String>,
    pub port: Option<u16>,
}

impl Config{
    pub fn load_config(config_path: PathBuf) -> Result<Self, Box<dyn std::error::Error>> {
        let config_str = fs::read_to_string(config_path)?;
        let config = toml::from_str(&config_str)?;
        Ok(config)
    }
}