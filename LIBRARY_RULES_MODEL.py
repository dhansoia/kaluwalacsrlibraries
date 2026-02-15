# ADD TO models.py

class UserRulesAcknowledgment(db.Model):
    __tablename__ = 'user_rules_acknowledgment'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    library_id = db.Column(db.Integer, db.ForeignKey('library.id'), nullable=False)
    acknowledged_at = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45), nullable=True)
    
    # Relationships
    user = db.relationship('User', backref='rules_acknowledgments')
    library = db.relationship('Library', backref='rules_acknowledgments')
    
    # Unique constraint - one acknowledgment per user per library
    __table_args__ = (
        db.UniqueConstraint('user_id', 'library_id', name='unique_user_library_ack'),
    )
    
    def __repr__(self):
        return f'<RulesAck User:{self.user_id} Library:{self.library_id}>'

# Also add this field to SystemSettings model:
# library_rules = db.Column(db.Text, nullable=True)  # JSON or text with rules
