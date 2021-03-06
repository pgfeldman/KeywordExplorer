-- MariaDB dump 10.19  Distrib 10.4.19-MariaDB, for Win64 (AMD64)
--
-- Host: localhost    Database: twitter_v2
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
-- Temporary table structure for view `keyword_tweet_view`
--

DROP TABLE IF EXISTS `keyword_tweet_view`;
/*!50001 DROP VIEW IF EXISTS `keyword_tweet_view`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `keyword_tweet_view` (
  `name` tinyint NOT NULL,
  `start` tinyint NOT NULL,
  `end` tinyint NOT NULL,
  `keywords` tinyint NOT NULL,
  `query` tinyint NOT NULL,
  `keyword` tinyint NOT NULL,
  `author_id` tinyint NOT NULL,
  `conversation_id` tinyint NOT NULL,
  `text` tinyint NOT NULL
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
  `name` varchar(255) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `sample_start` datetime DEFAULT NULL,
  `sample_end` datetime DEFAULT NULL,
  `keywords` text DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `table_experiment`
--

LOCK TABLES `table_experiment` WRITE;
/*!40000 ALTER TABLE `table_experiment` DISABLE KEYS */;
/*!40000 ALTER TABLE `table_experiment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `table_query`
--

DROP TABLE IF EXISTS `table_query`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `table_query` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `experiment_id` int(11) DEFAULT NULL,
  `query` text DEFAULT NULL,
  `keyword` varchar(255) DEFAULT NULL,
  `start_time` datetime DEFAULT NULL,
  `end_time` datetime DEFAULT NULL,
  `date_executed` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `table_query`
--

LOCK TABLES `table_query` WRITE;
/*!40000 ALTER TABLE `table_query` DISABLE KEYS */;
/*!40000 ALTER TABLE `table_query` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `table_tweet`
--

DROP TABLE IF EXISTS `table_tweet`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `table_tweet` (
  `row_id` int(11) NOT NULL AUTO_INCREMENT,
  `query_id` int(11) DEFAULT NULL,
  `author_id` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `in_reply_to_user_id` int(11) DEFAULT NULL,
  `lang` varchar(255) DEFAULT NULL,
  `id` int(11) NOT NULL,
  `text` text DEFAULT NULL,
  `conversation_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`row_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `table_tweet`
--

LOCK TABLES `table_tweet` WRITE;
/*!40000 ALTER TABLE `table_tweet` DISABLE KEYS */;
/*!40000 ALTER TABLE `table_tweet` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Final view structure for view `keyword_tweet_view`
--

/*!50001 DROP TABLE IF EXISTS `keyword_tweet_view`*/;
/*!50001 DROP VIEW IF EXISTS `keyword_tweet_view`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_unicode_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `keyword_tweet_view` AS select `te`.`name` AS `name`,`te`.`sample_start` AS `start`,`te`.`sample_end` AS `end`,`te`.`keywords` AS `keywords`,`tq`.`query` AS `query`,`tq`.`keyword` AS `keyword`,`tt`.`author_id` AS `author_id`,`tt`.`conversation_id` AS `conversation_id`,`tt`.`text` AS `text` from ((`table_experiment` `te` join `table_query` `tq` on(`te`.`id` = `tq`.`experiment_id`)) join `table_tweet` `tt` on(`tq`.`id` = `tt`.`query_id`)) */;
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

-- Dump completed on 2022-07-05 16:52:33
