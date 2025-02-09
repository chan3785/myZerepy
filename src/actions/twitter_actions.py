import time ,os
from dotenv import load_dotenv
from src.action_handler import register_action
from src.helpers import print_h_bar
from src.prompts import POST_TWEET_PROMPT, REPLY_TWEET_PROMPT


@register_action("post-tweet")
def post_tweet(agent, **kwargs):
    current_time = time.time()

    if ("last_tweet_time" not in agent.context):
        last_tweet_time = 0
    else:
        last_tweet_time = agent.context["last_tweet_time"]

    if current_time - last_tweet_time >= agent.tweet_interval:
        agent.logger.info("\n📝 GENERATING NEW TWEET")
        print_h_bar()

        prompt = POST_TWEET_PROMPT.format(agent_name = agent.name)
        tweet_text = agent.prompt_llm(prompt)

        if tweet_text:
            agent.logger.info("\n🚀 Posting tweet:")
            agent.logger.info(f"'{tweet_text}'")
            agent.connection_manager.perform_action(
                connection_name="twitter",
                action_name="post-tweet",
                params=[tweet_text]
            )
            agent.context["last_tweet_time"] = current_time
            agent.logger.info("\n✅ Tweet posted successfully!")
            return True
    else:
        agent.logger.info("\n👀 Delaying post until tweet interval elapses...")
        return False


@register_action("reply-to-tweet")
def reply_to_tweet(agent, **kwargs):
    if "timeline_tweets" in agent.context and agent.context["timeline_tweets"] is not None and len(agent.context["timeline_tweets"]) > 0:
        tweet = agent.context["timeline_tweets"].pop(0)
        tweet_id = tweet.get('id')
        if not tweet_id:
            return

        agent.logger.info(f"\n💬 GENERATING REPLY to: {tweet.get('text', '')[:50]}...")

        base_prompt = REPLY_TWEET_PROMPT.format(tweet_text =tweet.get('text') )
        reply_text = agent.prompt_llm(prompt=base_prompt)

        if reply_text:
            agent.logger.info(f"\n🚀 Posting reply: '{reply_text}'")
            agent.connection_manager.perform_action(
                connection_name="twitter",
                action_name="reply-to-tweet",
                params=[tweet_id, reply_text]
            )
            agent.logger.info("✅ Reply posted successfully!")
            return True
    else:
        agent.logger.info("\n👀 No tweets found to reply to...")
        return False

@register_action("like-tweet")
def like_tweet(agent, **kwargs):
    if "timeline_tweets" in agent.context and agent.context["timeline_tweets"] is not None and len(agent.context["timeline_tweets"]) > 0:
        tweet = agent.context["timeline_tweets"].pop(0)
        tweet_id = tweet.get('id')
        if not tweet_id:
            return False
        
        load_dotenv()
        username = os.getenv('TWITTER_USERNAME', '').lower()

        is_own_tweet = tweet.get('author_username', '').lower() == username
        if is_own_tweet:
            replies = agent.connection_manager.perform_action(
                connection_name="twitter",
                action_name="get-tweet-replies",
                params=[tweet.get('author_id')]
            )
            if replies:
                agent.context["timeline_tweets"].extend(replies[:agent.own_tweet_replies_count])
            return True 

        agent.logger.info(f"\n👍 LIKING TWEET: {tweet.get('text', '')[:50]}...")

        agent.connection_manager.perform_action(
            connection_name="twitter",
            action_name="like-tweet",
            params=[tweet_id]
        )
        agent.logger.info("✅ Tweet liked successfully!")
        return True
    else:
        agent.logger.info("\n👀 No tweets found to like...")
    return False
