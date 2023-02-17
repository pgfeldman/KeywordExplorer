-- MariaDB dump 10.19  Distrib 10.4.19-MariaDB, for Win64 (AMD64)
--
-- Host: localhost    Database: gpt_summary
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
-- Temporary table structure for view `source_text_view`
--

DROP TABLE IF EXISTS `source_text_view`;
/*!50001 DROP VIEW IF EXISTS `source_text_view`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `source_text_view` (
  `source_id` tinyint NOT NULL,
  `text_name` tinyint NOT NULL,
  `group_name` tinyint NOT NULL,
  `text_id` tinyint NOT NULL,
  `summary_id` tinyint NOT NULL,
  `parsed_text` tinyint NOT NULL,
  `embedding` tinyint NOT NULL
) ENGINE=MyISAM */;
SET character_set_client = @saved_cs_client;

--
-- Temporary table structure for view `summary_text_view`
--

DROP TABLE IF EXISTS `summary_text_view`;
/*!50001 DROP VIEW IF EXISTS `summary_text_view`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `summary_text_view` (
  `proj_id` tinyint NOT NULL,
  `text_name` tinyint NOT NULL,
  `group_name` tinyint NOT NULL,
  `text_id` tinyint NOT NULL,
  `summary_id` tinyint NOT NULL,
  `level` tinyint NOT NULL,
  `parsed_text` tinyint NOT NULL,
  `embedding` tinyint NOT NULL,
  `origins` tinyint NOT NULL
) ENGINE=MyISAM */;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `table_parsed_text`
--

DROP TABLE IF EXISTS `table_parsed_text`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `table_parsed_text` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `source` int(11) DEFAULT NULL,
  `summary_id` int(11) DEFAULT -1,
  `parsed_text` text DEFAULT NULL,
  `embedding` blob DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10487 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `table_source`
--

DROP TABLE IF EXISTS `table_source`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `table_source` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `text_name` varchar(255) DEFAULT NULL,
  `group_name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1 COMMENT='The source doc for the parsed text';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `table_summary_text`
--

DROP TABLE IF EXISTS `table_summary_text`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `table_summary_text` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `source` int(11) DEFAULT NULL,
  `level` int(11) DEFAULT NULL,
  `summary_id` int(11) DEFAULT -1,
  `summary_text` text DEFAULT NULL,
  `embedding` blob DEFAULT NULL,
  `origins` text DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Final view structure for view `source_text_view`
--

/*!50001 DROP TABLE IF EXISTS `source_text_view`*/;
/*!50001 DROP VIEW IF EXISTS `source_text_view`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_unicode_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `source_text_view` AS select `s`.`id` AS `source_id`,`s`.`text_name` AS `text_name`,`s`.`group_name` AS `group_name`,`p`.`id` AS `text_id`,`p`.`summary_id` AS `summary_id`,`p`.`parsed_text` AS `parsed_text`,`p`.`embedding` AS `embedding` from (`table_source` `s` join `table_parsed_text` `p` on(`p`.`source` = `s`.`id`)) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `summary_text_view`
--

/*!50001 DROP TABLE IF EXISTS `summary_text_view`*/;
/*!50001 DROP VIEW IF EXISTS `summary_text_view`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_unicode_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `summary_text_view` AS select `ts`.`id` AS `proj_id`,`ts`.`text_name` AS `text_name`,`ts`.`group_name` AS `group_name`,`tst`.`id` AS `text_id`,`tst`.`summary_id` AS `summary_id`,`tst`.`level` AS `level`,`tst`.`summary_text` AS `parsed_text`,`tst`.`embedding` AS `embedding`,`tst`.`origins` AS `origins` from (`table_summary_text` `tst` join `table_source` `ts` on(`tst`.`source` = `ts`.`id`)) */;
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

-- Dump completed on 2023-02-17 10:52:54
