CREATE SCHEMA IF NOT EXISTS `mydb` DEFAULT CHARACTER SET utf8 ;
USE `mydb` ;

CREATE TABLE IF NOT EXISTS `mydb`.`rooms` (
  `id` INT NOT NULL,
  `name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `mydb`.`students` (
  `id` INT NOT NULL,
  `name` VARCHAR(45) NOT NULL,
  `room` INT NOT NULL,
  `sex` CHAR(1) NOT NULL,
  `birthday` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_students_1_idx` (`room` ASC),
  CONSTRAINT `fk_students`
    FOREIGN KEY (`room`)
    REFERENCES `mydb`.`rooms` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;
