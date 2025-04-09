from posts.models import Post

class PostFactory:
    @staticmethod
    def create_post(post_type, title, content='', metadata=None):
        if metadata is None:
            metadata = {}

        if post_type == 'text':
            return Post.objects.create(post_type=post_type, title=title, content=content, metadata=metadata)
        elif post_type == 'image':
            return Post.objects.create(post_type=post_type, title=title, metadata=metadata)
        else:
            raise ValueError("Unsupported post type.")