-- Création de l'utilisateur
CREATE USER 'epsinformation'@'localhost';
GRANT ALL ON epsinformation TO 'epsinformation'@'localhost' IDENTIFIED BY 'epsinformation'; 
FLUSH PRIVILEGES;

-- Création de la base de données
CREATE DATABASE IF NOT EXISTS `epsinformation`;
USE `epsinformation`;

-- Table compte
CREATE TABLE `compte` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `role` TINYINT NOT NULL,
  `username` VARCHAR(255) NOT NULL,
  `nom` VARCHAR(255) NOT NULL,
  `prenom` VARCHAR(255) NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  `password` VARCHAR(512) NOT NULL,
  PRIMARY KEY (`id`)
);

-- Table format
CREATE TABLE `format` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `libelle` VARCHAR(255) NULL,
  PRIMARY KEY (`id`)
) COMMENT 'format des images';

-- Table image
CREATE TABLE `image` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `contenu` MEDIUMBLOB NOT NULL,
  `id_format` INT NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `FK_format_TO_image` FOREIGN KEY (`id_format`) REFERENCES `format` (`id`)
);

-- Table post
CREATE TABLE `post` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `titre` VARCHAR(255) NULL,
  `description` TEXT NULL,
  `date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'ajouter un défaut',
  `id_compte` INT NOT NULL,
  `degre` INT NULL,
  `id_type` INT NOT NULL,
  `date_debut` DATE NULL,
  `date_fin` DATE NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `FK_compte_TO_post` FOREIGN KEY (`id_compte`) REFERENCES `compte` (`id`),
  CONSTRAINT `FK_type_TO_post` FOREIGN KEY (`id_type`) REFERENCES `type` (`id`)
);

-- Table post_image
CREATE TABLE `post_image` (
  `id_post` INT NOT NULL,
  `id_image` INT NOT NULL,
  PRIMARY KEY (`id_post`, `id_image`),
  CONSTRAINT `FK_post_TO_post_image` FOREIGN KEY (`id_post`) REFERENCES `post` (`id`),
  CONSTRAINT `FK_image_TO_post_image` FOREIGN KEY (`id_image`) REFERENCES `image` (`id`)
);

-- Table type
CREATE TABLE `type` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `intitule` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id`)
);
