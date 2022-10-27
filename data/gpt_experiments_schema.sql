-- MariaDB dump 10.19  Distrib 10.4.19-MariaDB, for Win64 (AMD64)
--
-- Host: localhost    Database: gpt_experiments
-- ------------------------------------------------------
-- Server version	10.4.19-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Temporary table structure for view `combined`
--

DROP TABLE IF EXISTS `combined`;
/*!50001 DROP VIEW IF EXISTS `combined`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `combined` (
  `root_id` tinyint NOT NULL,
  `experiment_id` tinyint NOT NULL,
  `probe` tinyint NOT NULL,
  `date` tinyint NOT NULL,
  `text` tinyint NOT NULL
) ENGINE=MyISAM */;
SET character_set_client = @saved_cs_client;

--
-- Temporary table structure for view `model_combined`
--

DROP TABLE IF EXISTS `model_combined`;
/*!50001 DROP VIEW IF EXISTS `model_combined`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `model_combined` (
  `experiment_id` tinyint NOT NULL,
  `model_name` tinyint NOT NULL,
  `probe` tinyint NOT NULL,
  `content` tinyint NOT NULL
) ENGINE=MyISAM */;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `table_experiment`
--

DROP TABLE IF EXISTS `table_experiment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `table_experiment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `description` text DEFAULT NULL,
  `model_name` varchar(255) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `probe_list` text DEFAULT NULL,
  `batch_size` int(11) DEFAULT NULL,
  `do_sample` tinyint(1) DEFAULT NULL,
  `max_length` int(11) DEFAULT NULL,
  `top_k` int(11) DEFAULT NULL,
  `top_p` float DEFAULT NULL,
  `num_return_sequences` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=123 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `table_output`
--

DROP TABLE IF EXISTS `table_output`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `table_output` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `experiment_id` int(11) DEFAULT NULL,
  `root_id` int(11) DEFAULT NULL,
  `tag` varchar(255) DEFAULT NULL,
  `depth` int(11) DEFAULT NULL,
  `probe` text DEFAULT NULL,
  `content` text DEFAULT NULL,
  `before_regex` varchar(255) DEFAULT NULL,
  `after_regex` varchar(255) DEFAULT NULL,
  `parts_of_speech` text DEFAULT NULL,
  `sent_val` float DEFAULT 0,
  `sent_label` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=374525 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `table_text`
--

DROP TABLE IF EXISTS `table_text`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `table_text` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `experiment_id` int(11) DEFAULT NULL,
  `probe` text DEFAULT NULL,
  `text` text DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `table_text_data`
--

DROP TABLE IF EXISTS `table_text_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `table_text_data` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `text_id` int(11) DEFAULT NULL,
  `name` varchar(128) DEFAULT NULL,
  `value` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=80 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary table structure for view `test_view`
--

DROP TABLE IF EXISTS `test_view`;
/*!50001 DROP VIEW IF EXISTS `test_view`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `test_view` (
  `id` tinyint NOT NULL,
  `experiment_id` tinyint NOT NULL,
  `probe` tinyint NOT NULL,
  `text` tinyint NOT NULL,
  `keyword` tinyint NOT NULL,
  `created` tinyint NOT NULL,
  `location` tinyint NOT NULL,
  `probability` tinyint NOT NULL
) ENGINE=MyISAM */;
SET character_set_client = @saved_cs_client;

--
-- Final view structure for view `combined`
--

/*!50001 DROP TABLE IF EXISTS `combined`*/;
/*!50001 DROP VIEW IF EXISTS `combined`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_unicode_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `combined` AS select distinct `t_1`.`root_id` AS `root_id`,`t_1`.`experiment_id` AS `experiment_id`,`t_1`.`probe` AS `probe`,`t_1`.`content` AS `date`,`t_2`.`content` AS `text` from (`table_output` `t_1` join `table_output` `t_2` on(`t_1`.`root_id` = `t_2`.`root_id` and `t_1`.`tag` = 'date' and `t_2`.`tag` = 'trimmed')) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `model_combined`
--

/*!50001 DROP TABLE IF EXISTS `model_combined`*/;
/*!50001 DROP VIEW IF EXISTS `model_combined`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_unicode_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `model_combined` AS select `o`.`experiment_id` AS `experiment_id`,`e`.`model_name` AS `model_name`,`o`.`probe` AS `probe`,`o`.`content` AS `content` from (`table_output` `o` join `table_experiment` `e` on(`o`.`experiment_id` = `e`.`id`)) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `test_view`
--

/*!50001 DROP TABLE IF EXISTS `test_view`*/;
/*!50001 DROP VIEW IF EXISTS `test_view`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_unicode_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `test_view` AS select `tt`.`id` AS `id`,`tt`.`experiment_id` AS `experiment_id`,`tt`.`probe` AS `probe`,`tt`.`text` AS `text`,`ttd_k`.`value` AS `keyword`,`ttd_c`.`value` AS `created`,`ttd_l`.`value` AS `location`,`ttd_p`.`value` AS `probability` from ((((`table_text` `tt` join `table_text_data` `ttd_c` on(`tt`.`id` = `ttd_c`.`text_id` and `ttd_c`.`name` = 'created')) join `table_text_data` `ttd_k` on(`tt`.`id` = `ttd_k`.`text_id` and `ttd_k`.`name` = 'keyword')) join `table_text_data` `ttd_l` on(`tt`.`id` = `ttd_l`.`text_id` and `ttd_l`.`name` = 'location')) join `table_text_data` `ttd_p` on(`tt`.`id` = `ttd_p`.`text_id` and `ttd_p`.`name` = 'probability')) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-10-27 11:19:16
