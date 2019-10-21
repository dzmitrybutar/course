ALTER TABLE `mydb`.`students` 
ADD INDEX `students_3_idx` (`room` ASC, `sex` ASC),
ADD INDEX `students_2_idx` (`room` ASC, `birthday` ASC);
